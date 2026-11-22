// reset_lockout.js — Reset bo dem dang nhap sai + mo khoa tai khoan trong SQLite
// Cach dung: node reset_lockout.js
const sqlite3 = require("/home/z/my-project/eshop-sut/backend/node_modules/sqlite3").verbose();
const db = new sqlite3.Database("/home/z/my-project/eshop-sut/backend/database.sqlite");
db.run("UPDATE users SET login_attempts = 0, locked_until = NULL", function (err) {
  if (err) { console.error("ERROR:", err.message); process.exit(1); }
  console.log(`[reset_lockout] Da reset login_attempts=0, locked_until=NULL cho ${this.changes} users`);
  db.close(() => process.exit(0));
});
