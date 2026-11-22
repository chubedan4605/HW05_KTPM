#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_testplans.py — Sinh 4 JMeter test plan (.jmx) cho HW05 Performance Testing
SUT: EShop (Node.js + Express + SQLite) — localhost:3000
Workflow E2E: Login -> Search -> Product Detail -> Add to Cart -> Checkout

Plans (dung ten {StudentID}_{ScenarioType}_{YYYYMMDD}):
  23120279_Load_20261122.jmx   — 50 VU, ramp 120s, duration 420s, think ~1s (Summary Report)
  23120279_Stress_20261122.jmx — 8 bac thang x 25 VU (25->200), moi bac 60s, think ~0.3s (Aggregate Report)
  23120279_Spike_20261122.jmx  — baseline 10 VU + 3 dot spike 100 VU trong 35s (View Results Tree)
  23120279_Soak_20261122.jmx   — 25 VU, 900s (15 phut) de tim endurance threshold (View Results in Table)
"""
import os

SID = "23120279"
DATE = "20261122"
OUT = "/home/z/my-project/hw05/testplans"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- helpers
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def csv_dataset(name, fname, vars_):
    return f'''<CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet" testname="{name}" enabled="true">
          <stringProp name="filename">data/{fname}</stringProp>
          <stringProp name="fileEncoding">UTF-8</stringProp>
          <stringProp name="variableNames">{vars_}</stringProp>
          <boolProp name="ignoreFirstLine">true</boolProp>
          <stringProp name="delimiter">,</stringProp>
          <boolProp name="quotedData">false</boolProp>
          <boolProp name="recycle">true</boolProp>
          <boolProp name="stopThread">false</boolProp>
          <stringProp name="shareMode">shareMode.all</stringProp>
        </CSVDataSet>
        <hashTree/>'''

def http_defaults():
    return '''<ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP Request Defaults (EShop API)" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain">localhost</stringProp>
          <stringProp name="HTTPSampler.port">3000</stringProp>
          <stringProp name="HTTPSampler.protocol">http</stringProp>
          <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
          <stringProp name="HTTPSampler.path"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout">5000</stringProp>
          <stringProp name="HTTPSampler.response_timeout">10000</stringProp>
        </ConfigTestElement>
        <hashTree/>'''

def header_manager(name, headers):
    rows = ""
    for k, v in headers:
        rows += f'''<elementProp name="" elementType="Header">
              <stringProp name="Header.name">{k}</stringProp>
              <stringProp name="Header.value">{v}</stringProp>
            </elementProp>\n'''
    return f'''<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="{name}" enabled="true">
          <collectionProp name="HeaderManager.headers">
            {rows}          </collectionProp>
        </HeaderManager>
        <hashTree/>'''

def ra_code(name, code="200"):
    return f'''<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="RA {name}: HTTP {code}" enabled="true">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="-1400441695">{code}</stringProp>
            </collectionProp>
            <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
            <boolProp name="Assertion.assume_success">false</boolProp>
            <intProp name="Assertion.test_type">8</intProp>
          </ResponseAssertion>
          <hashTree/>'''

def ra_contains(name, text):
    return f'''<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="RA {name}: contains &quot;{esc(text)}&quot;" enabled="true">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="1493335975">{esc(text)}</stringProp>
            </collectionProp>
            <stringProp name="Assertion.test_field">Assertion.response_data</stringProp>
            <boolProp name="Assertion.assume_success">false</boolProp>
            <intProp name="Assertion.test_type">16</intProp>
          </ResponseAssertion>
          <hashTree/>'''

def duration_assert(name, ms):
    return f'''<DurationAssertion guiclass="DurationAssertionGui" testclass="DurationAssertion" testname="DA {name}: &lt;= {ms}ms" enabled="true">
            <stringProp name="DurationAssertion.duration">{ms}</stringProp>
          </DurationAssertion>
          <hashTree/>'''

def json_extractor(name, refs, paths, defaults):
    ref_s = ";".join(refs); path_s = ";".join(paths); def_s = ";".join(defaults)
    return f'''<JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="JPE {name}" enabled="true">
            <stringProp name="JSONPostProcessor.referenceNames">{ref_s}</stringProp>
            <stringProp name="JSONPostProcessor.jsonPathExprs">{path_s}</stringProp>
            <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
            <stringProp name="JSONPostProcessor.defaultValues">{def_s}</stringProp>
          </JSONPostProcessor>
          <hashTree/>'''

def raw_body(body_json):
    return f'''<elementProp name="" elementType="HTTPArgument">
              <boolProp name="HTTPArgument.always_encode">false</boolProp>
              <stringProp name="Argument.value">{body_json}</stringProp>
              <stringProp name="Argument.metadata">=</stringProp>
            </elementProp>'''

def get_param(pname, pval):
    return f'''<elementProp name="" elementType="HTTPArgument">
              <boolProp name="HTTPArgument.always_encode">true</boolProp>
              <stringProp name="Argument.name">{pname}</stringProp>
              <stringProp name="Argument.value">{pval}</stringProp>
              <stringProp name="Argument.metadata">=</stringProp>
              <stringProp name="Argument.use_equals">true</stringProp>
            </elementProp>'''

def sampler(name, method, path, args_xml, body_raw=False):
    post = "true" if body_raw else "false"
    return f'''<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="{name}" enabled="true">
          <boolProp name="HTTPSampler.postBodyRaw">{post}</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments">
            <collectionProp name="Arguments.arguments">
              {args_xml}            </collectionProp>
          </elementProp>
          <stringProp name="HTTPSampler.path">{path}</stringProp>
          <stringProp name="HTTPSampler.method">{method}</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        </HTTPSamplerProxy>'''

def timer(constant, range_ms):
    return f'''<GaussianRandomTimer guiclass="GaussianRandomTimerGui" testclass="GaussianRandomTimer" testname="Think time (Gaussian {constant}+/-{range_ms}ms)" enabled="true">
          <stringProp name="ConstantTimer.delay">{constant}</stringProp>
          <stringProp name="RandomTimer.range">{range_ms}</stringProp>
        </GaussianRandomTimer>
        <hashTree/>'''

SAVE_CFG = '''<objProp>
          <name>saveConfig</name>
          <value class="SampleSaveConfiguration">
            <time>true</time>
            <latency>true</latency>
            <timestamp>true</timestamp>
            <success>true</success>
            <label>true</label>
            <code>true</code>
            <message>true</message>
            <threadName>true</threadName>
            <dataType>true</dataType>
            <encoding>false</encoding>
            <assertions>true</assertions>
            <subresults>true</subresults>
            <responseData>false</responseData>
            <samplerData>false</samplerData>
            <xml>false</xml>
            <fieldNames>true</fieldNames>
            <responseHeaders>false</responseHeaders>
            <requestHeaders>false</requestHeaders>
            <responseDataOnError>true</responseDataOnError>
            <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
            <assertionsResultsToSave>0</assertionsResultsToSave>
            <bytes>true</bytes>
            <sentBytes>true</sentBytes>
            <url>true</url>
            <threadCounts>true</threadCounts>
            <idleTime>true</idleTime>
            <connectTime>true</connectTime>
          </value>
        </objProp>'''

def listener(gui, name):
    return f'''<ResultCollector guiclass="{gui}" testclass="ResultCollector" testname="{name}" enabled="true">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          {SAVE_CFG}
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>'''

def thread_group(name, threads, ramp, duration, delay, body_xml):
    return f'''<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="{name}" enabled="true">
          <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
          <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController">
            <boolProp name="LoopController.continue_forever">true</boolProp>
            <stringProp name="LoopController.loops">-1</stringProp>
          </elementProp>
          <stringProp name="ThreadGroup.num_threads">{threads}</stringProp>
          <stringProp name="ThreadGroup.ramp_time">{ramp}</stringProp>
          <boolProp name="ThreadGroup.scheduler">true</boolProp>
          <stringProp name="ThreadGroup.duration">{duration}</stringProp>
          <stringProp name="ThreadGroup.delay">{delay}</stringProp>
          <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
        </ThreadGroup>
        <hashTree>
          {body_xml}        </hashTree>'''

def transaction(body_xml):
    return f'''<TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="TC_E2E_Mua_hang" enabled="true">
          <boolProp name="TransactionController.includeTimers">false</boolProp>
        </TransactionController>
        <hashTree>
          {body_xml}        </hashTree>'''

# ---------------------------------------------------------------- workflow (correlated E2E)
def workflow(think_c, think_r, indent="          "):
    """5 sampler cua workflow E2E + timer + header.
    Moi sampler co hashTree rieng chua post-processor/assertion cua no (dung cu phap JMeter)."""
    i2 = indent + "  "

    def unit(sampler_xml, *children):
        inner = "".join(children)
        return sampler_xml + "\n" + i2 + "<hashTree>\n" + inner + i2 + "</hashTree>\n"

    # 01 LOGIN (auth-heavy) — FR-02
    login = unit(
        sampler("API01_Login_auth", "POST", "/api/login",
                raw_body('{\n  "email": "${email}",\n  "password": "${password}"\n}'), body_raw=True),
        json_extractor("token+userId", ["token", "userId"], ["$.token", "$.user.id"], ["TOKEN_NOT_FOUND", "-1"]),
        ra_code("Login", "200"),
        ra_contains("Login", "Login successful"),
        duration_assert("Login", 3000))
    # 02 SEARCH (read-heavy) — FR-05
    search = unit(
        sampler("API02_Search_products_read", "GET", "/api/products", get_param("search", "${keyword}")),
        json_extractor("productId+price+name", ["productId", "prodPrice", "prodName"],
                       ["$[0].id", "$[0].price", "$[0].name"],
                       ["${product_id}", "${price}", "${product_name}"]),
        ra_code("Search", "200"),
        ra_contains("Search", "${keyword}"),
        duration_assert("Search", 2000))
    # 03 DETAIL (read-heavy) — FR-06
    detail = unit(
        sampler("API03_Product_detail_read", "GET", "/api/products/${productId}", ""),
        ra_code("Detail", "200"),
        ra_contains("Detail", "${prodName}"),
        duration_assert("Detail", 2000))
    # 04 ADD TO CART (transactional) — FR-07
    cart = unit(
        sampler("API04_Add_to_cart_txn", "POST", "/api/cart",
                raw_body('{\n  "id": ${productId},\n  "name": "${prodName}",\n  "price": ${prodPrice},\n  "quantity": ${__Random(1,3)}\n}'), body_raw=True),
        ra_code("Cart", "200"),
        ra_contains("Cart", "Added to cart"),
        duration_assert("Cart", 3000))
    # 05 CHECKOUT (transactional) — FR-08
    checkout = unit(
        sampler("API05_Checkout_txn", "POST", "/api/checkout",
                raw_body('{\n  "total_amount": ${prodPrice},\n  "shipping_address": "123 Le Loi, Q1, TP.HCM"\n}'), body_raw=True),
        json_extractor("orderId", ["orderId"], ["$.orderId"], ["-1"]),
        ra_code("Checkout", "200"),
        ra_contains("Checkout", "Checkout successful"),
        duration_assert("Checkout", 5000))

    hdr = header_manager("HM Auth+JSON", [("Content-Type", "application/json"), ("Authorization", "Bearer ${token}")])
    tmr = timer(think_c, think_r)
    return transaction(hdr + tmr + login + search + detail + cart + checkout)

# ---------------------------------------------------------------- plan assembly
def build_plan(plan_name, comments, groups_xml, listener_xml):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="{plan_name}" enabled="true">
      <stringProp name="TestPlan.comments">{esc(comments)}</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      {csv_dataset("CSV users.csv (credentials)", "users.csv", "email,password")}
      {csv_dataset("CSV products.csv (search data)", "products.csv", "keyword,product_id,product_name,price")}
      {http_defaults()}
      {groups_xml}
      {listener_xml}    </hashTree>
  </hashTree>
</jmeterTestPlan>
'''

# ---- 1. LOAD PLAN: 50 VU, ramp 120s, 420s, think 1000+/-500ms, Summary Report
load_body = workflow(1000, 500)
load_tg = thread_group("Load_50VU_ramp120_dur420", 50, 120, 420, 0, load_body)
load_plan = build_plan(
    f"{SID}_Load_{DATE}",
    "Load test — EShop E2E (Login->Search->Detail->AddToCart->Checkout). "
    "50 VU, ramp-up 120s, duration 420s (5 phut o dang on dinh), think time Gaussian 1000+/-500ms. "
    "Listener: Summary Report. Author: 23120279 — AI-assisted (GLM), human-reviewed.",
    load_tg, listener("SummaryReport", "Summary Report"))

# ---- 2. STRESS PLAN (v2): 8 bac x 60 VU (60->480), moi bac 60s, think 50+/-50ms, Aggregate Report
stress_tgs = ""
for k in range(8):
    delay = 60 * k
    dur = 480 - 60 * k
    stress_tgs += thread_group(f"Stress_Step{k+1}_plus60VU_total{(k+1)*60}", 60, 5, dur, delay, workflow(50, 50))
stress_plan = build_plan(
    f"{SID}_Stress_{DATE}",
    "Stress test (v2 — sau khi v1 25->200 VU voi think 300ms khong tim thay diem gay, da tang bien do) — "
    "EShop E2E. Bac thang 60->120->...->480 VU, moi bac 60s (tong 480s), think time Gaussian 50+/-50ms. "
    "Listener: Aggregate Report. Author: 23120279 — AI-assisted (GLM), human-reviewed.",
    stress_tgs, listener("StatVisualizer", "Aggregate Report"))

# ---- 3. SPIKE PLAN (v2): baseline 20 VU (300s) + 3 dot spike len 300 VU (35s), VRT
spike_tgs = thread_group("Spike_Baseline_20VU_dur240", 20, 2, 240, 0, workflow(1000, 500))
for w in range(2):
    delay = 30 + 90 * w
    spike_tgs += thread_group(f"Spike_Wave{w+1}_total300VU_dur40", 280, 10, 40, delay, workflow(50, 50))
spike_plan = build_plan(
    f"{SID}_Spike_{DATE}",
    "Spike test (FINAL) — EShop E2E. "
    "Baseline 20 VU (240s) + 2 dot spike len 300 VU (ramp 10s, duy tri 40s, delay 30/120s). "
    "Ghi chu: 3 song 280 VU khong kha thi tren may nay vi /proc/sys/kernel/threads-max = 925 "
    "(860+ Java thread + node + he thong vuot nguong — ThreadStarter chet im lang khi Thread.start() neng Error). "
    "Listener: View Results Tree. Author: 23120279 — AI-assisted (GLM), human-reviewed.",
    spike_tgs, listener("ViewResultsFullVisualizer", "View Results Tree"))

# ---- 4. SOAK PLAN (v2): 180 VU (≈75% suc chua tai diem goi), 900s, think 100+/-100ms, View Results in Table
soak_tg = thread_group("Soak_180VU_dur900", 180, 30, 900, 0, workflow(100, 100))
soak_plan = build_plan(
    f"{SID}_Soak_{DATE}",
    "Soak/Endurance test (v2 — tai duy tri ≈75% diem goi tim duoc tu Stress) — EShop E2E. "
    "180 VU lien tuc 900s (15 phut), think Gaussian 100+/-100ms, muc tieu: xac nhan nguong ben bieu "
    "(max stable RPS) va tran bo nho (memory ceiling). Listener: View Results in Table. "
    "Author: 23120279 — AI-assisted (GLM), human-reviewed.",
    soak_tg, listener("TableVisualizer", "View Results in Table"))

for fname, content in [
    (f"{SID}_Load_{DATE}.jmx", load_plan),
    (f"{SID}_Stress_{DATE}.jmx", stress_plan),
    (f"{SID}_Spike_{DATE}.jmx", spike_plan),
    (f"{SID}_Soak_{DATE}.jmx", soak_plan),
]:
    p = os.path.join(OUT, fname)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {p} ({os.path.getsize(p)} bytes)")
print("DONE")
