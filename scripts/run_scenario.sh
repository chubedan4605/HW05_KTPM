#!/bin/bash
# run_scenario.sh <Load|Stress|Spike|Soak> — Chay 1 kich ban JMeter kem giam sat tai Nguyen
# Ket qua: results/<name>/23120279_<name>_20261122.jtl + html/ + evidence/mon/<name>_*.log
set -e
NAME=$1
SID=23120279
DATE=20261122
HW=/home/z/my-project/hw05
JM=/home/z/my-project/tools/apache-jmeter-5.6.3/bin/jmeter
JMX="$HW/testplans/${SID}_${NAME}_${DATE}.jmx"
JTL="$HW/results/${NAME,,}/${SID}_${NAME}_${DATE}.jtl"
HTML="$HW/results/${NAME,,}/html"
MON="$HW/evidence/mon"
JID=$(cat /home/z/my-project/.node_pid 2>/dev/null || pgrep -f "node server.js" | head -1)

if [ -z "$JID" ]; then echo "KHONG TIM THAY node server!"; exit 1; fi
echo "=== RUN $NAME | node PID=$JID | $(date) ==="

# Xoa ket qua cu (neu co)
rm -rf "$JTL" "$HTML" && mkdir -p "$HTML" "$MON"

# 1) Monitor tai Nguyen (CSV + HTML panel) — moi 5s
python3 /home/z/my-project/scripts/monitor.py --pid "$JID" \
  --out "$MON/${NAME}_resources.csv" --html "$MON/${NAME}_monitor.html" --interval 5 &
MON_PID=$!

# 2) Top snapshot moi 60s (nhin ca he thong: java + node)
( for i in $(seq 1 30); do
    echo "===== top snapshot $(date +%H:%M:%S) =====" >> "$MON/${NAME}_top_snapshots.log"
    top -b -n1 | head -22 >> "$MON/${NAME}_top_snapshots.log"
    sleep 60
  done ) &
TOP_PID=$!

# 3) Chay JMeter non-GUI + tao HTML dashboard (chay tu goc hw05/ de CSV path tuong doi dung)
cd "$HW"
export JVM_ARGS="-Xms512m -Xmx2048m"  # fix heap: ThreadStarter bi OOM o song thu 3 voi heap mac dinh 1GB
"$JM" -n -t "$JMX" -l "$JTL" -e -o "$HTML" -j "$MON/${NAME}_jmeter_run.log" \
  2>&1 | tee "$MON/${NAME}_jmeter_console.log" | grep -E "^summary" | tail -40

# 4) Dung monitor
kill $MON_PID $TOP_PID 2>/dev/null || true
sleep 1
echo "=== DONE $NAME | $(date) ==="
echo "JTL: $JTL ($(wc -l < "$JTL") samples)"
echo "HTML: $HTML"
