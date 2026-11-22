#!/bin/bash
# full_reset.sh — Khoi phuc trang thai ban dau cho moi kich ban:
# 1) kill node server, 2) khoi dong lai (DB tu re-seed 5 san pham + 2 users),
# 3) chay lai seed (75 products + 100 users), 4) reset lockout, 5) smoke test
set -e
LOG=/home/z/my-project/backend.log

echo "[full_reset] 1) Dung node server..."
pkill -f "node server.js" 2>/dev/null || true
sleep 2

echo "[full_reset] 2) Khoi dong lai node server (DB re-seed tu dong)..."
cd /home/z/my-project/eshop-sut/backend
nohup node server.js > "$LOG" 2>&1 &
sleep 4
grep -q "Server is running" "$LOG" && echo "    OK: $LOG"

echo "[full_reset] 3) Seed du lieu (products + users)..."
cd /home/z/my-project
node scripts/seed_data.js | sed 's/^/    /'

echo "[full_reset] 4) Reset lockout..."
node scripts/reset_lockout.js | sed 's/^/    /'

echo "[full_reset] 5) Smoke test..."
TOKEN=$(curl -s -X POST http://localhost:3000/api/login -H "Content-Type: application/json" \
  -d '{"email":"perfuser001@eshop.test","password":"PerfTest123!"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")
echo "    Login OK, token: ${TOKEN:0:25}..."
echo "[full_reset] DONE"
