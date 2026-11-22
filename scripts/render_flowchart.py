#!/usr/bin/env python3
# render_flowchart.py — Chup flowchart HTML thanh PNG (full page, 2x) bang Playwright
from playwright.sync_api import sync_playwright

SRC = "file:///home/z/my-project/hw05/analysis/flowchart_continuous_testing.html"
OUT = "/home/z/my-project/hw05/analysis/flowchart_continuous_testing.png"

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-gpu"])
    pg = b.new_page(viewport={"width": 1040, "height": 1400}, device_scale_factor=2)
    pg.goto(SRC)
    pg.wait_for_timeout(1200)
    pg.screenshot(path=OUT, full_page=True)
    b.close()
print("OK:", OUT)
