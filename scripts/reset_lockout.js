// reset_lockout.js — Reset bo dem dang nhap sai + mo khoa tai khoan trong SQLite
// Cach dung: node scripts/reset_lockout.js
const path = require("path");
const backendDir = process.env.ESHOP_BACKEND || path.resolve(__dirname, "..", "..", "eshop-sut", "backend");
const sqlite3 = require(path.join(backendDir, "node_modules", "sqlite3")).verbose();
const db = new sqlite3.Database(path.join(backendDir, "database.sqlite"));
db.run("UPDATE users SET login_attempts = 0, locked_until = NULL", function (err) {
  if (err) { console.error("ERROR:", err.message); process.exit(1); }
  console.log(`[reset_lockout] Da reset login_attempts=0, locked_until=NULL cho ${this.changes} users`);
  db.close(() => process.exit(0));
});
