// seed_data.js — Dang ky users va import products cho EShop SUT qua API chinh thuc
// Chay: node seed_data.js  (backend phai dang chay tai localhost:3000)
const BASE = "http://localhost:3000";
const fs = require("fs");
const path = require("path");
const dataDir = path.resolve(__dirname, "..", "data");

async function post(path, body, token) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(BASE + path, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  const text = await res.text();
  let json; try { json = JSON.parse(text); } catch { json = text; }
  return { status: res.status, json };
}

// ---------- 1. Sinh danh sach san pham (~76) ----------
const catPhones = 1, catLaptops = 2, catAccess = 3;
const products = [];
const phoneModels = [
  ["iPhone 15 Pro Max", 30000000], ["iPhone 15 Pro", 26000000], ["iPhone 15", 22000000],
  ["iPhone 14 Pro Max", 25000000], ["iPhone 14", 18000000], ["iPhone 13", 15000000],
  ["Samsung Galaxy S24 Ultra", 28000000], ["Samsung Galaxy S24", 21000000],
  ["Samsung Galaxy S23 FE", 13000000], ["Samsung Galaxy A55", 9500000],
  ["Samsung Galaxy A35", 7200000], ["Xiaomi Redmi Note 13 Pro", 8500000],
  ["Xiaomi Redmi Note 13", 6500000], ["Xiaomi 14", 19000000], ["Xiaomi Poco X6 Pro", 9000000],
  ["Oppo Reno 11F", 8900000], ["Oppo A79", 6200000], ["Vivo V29", 9900000],
  ["Vivo Y28", 5200000], ["Realme 12 Pro", 8800000], ["Realme C67", 4500000],
  ["Google Pixel 8", 20500000], ["Nothing Phone 2", 16500000], ["Sony Xperia 5 V", 22000000],
];
const laptopModels = [
  ["MacBook Pro M3 Max", 65000000], ["MacBook Pro M3", 45000000], ["MacBook Air M3", 32000000],
  ["MacBook Air M2", 27000000], ["Laptop Dell XPS 15", 48000000], ["Laptop Dell Inspiron 15", 21000000],
  ["Laptop Dell Vostro 3530", 16500000], ["Laptop HP Spectre x360", 42000000],
  ["Laptop HP Pavilion 15", 19000000], ["Laptop HP Victus 16", 28500000],
  ["Laptop Lenovo ThinkPad X1 Carbon", 49000000], ["Laptop Lenovo IdeaPad Slim 5", 17500000],
  ["Laptop Lenovo Legion 5", 33000000], ["Laptop Asus Zenbook 14 OLED", 29500000],
  ["Laptop Asus Vivobook 15", 15500000], ["Laptop Asus ROG Strix G16", 45000000],
  ["Laptop Acer Aspire 5", 14900000], ["Laptop Acer Swift Go 14", 22500000],
  ["Laptop MSI Gaming Katana 15", 31000000], ["Laptop MSI Modern 14", 18000000],
  ["Laptop LG Gram 14", 34000000], ["Laptop Gigabyte G5", 29000000],
];
const accessModels = [
  ["Tai nghe AirPods Pro 2", 6000000], ["Tai nghe AirPods 3", 4300000],
  ["Tai nghe Samsung Galaxy Buds2 Pro", 4900000], ["Tai nghe Sony WH-1000XM5", 7900000],
  ["Tai nghe Sony WF-1000XM5", 6300000], ["Tai nghe Anker Soundcore Life Q30", 2200000],
  ["Tai nghe JBL Tune 770NC", 1900000], ["Tai nghe Xiaomi Buds 4 Pro", 3200000],
  ["Bàn phím cơ Keychron Q1", 4000000], ["Bàn phím cơ Keychron K2", 2500000],
  ["Bàn phím Logitech MX Keys S", 2900000], ["Bàn phím cơ Akko 5075B", 2100000],
  ["Bàn phím Razer BlackWidow V4", 3600000], ["Chuột Logitech MX Master 3S", 2500000],
  ["Chuột Logitech G Pro X Superlight", 2900000], ["Chuột Razer DeathAdder V3", 2200000],
  ["Chuột không dây Apple Magic Mouse", 2400000], ["Sạc nhanh Anker 65W GaN", 1200000],
  ["Sạc nhanh Ugreen 30W", 750000], ["Ốp lưng iPhone 15 Spigen", 450000],
  ["Ốp lưng Samsung S24 Slim Armor", 490000], ["Cáp sạc Anker USB-C 240W", 690000],
  ["Cáp sạc Ugreen Lightning 2m", 390000], ["Gậy chụp ảnh selfie Ugreen", 550000],
  ["Giá đỡ điện thoại Baseus", 350000], ["Miếng dán màn hình iPhone 15", 150000],
  ["Đồng hồ thông minh Apple Watch SE", 8500000], ["Đồng hồ thông minh Samsung Galaxy Watch 6", 7400000],
  ["Smartband Xiaomi Smart Band 8", 1100000],
];
for (const [name, price] of phoneModels) products.push({ name, price, description: `Điện thoại ${name} chính hãng, bảo hành 12 tháng`, imageUrl: "", category_id: catPhones });
for (const [name, price] of laptopModels) products.push({ name, price, description: `Laptop ${name} cấu hình mạnh cho học tập và làm việc`, imageUrl: "", category_id: catLaptops });
for (const [name, price] of accessModels) products.push({ name, price, description: `Phụ kiện ${name} chính hãng`, imageUrl: "", category_id: catAccess });

// ---------- 2. Dang ky 100 user perf ----------
const N_USERS = 100;
const PASSWORD = "PerfTest123!";
async function main() {
  // admin login de import san pham
  const adm = await post("/api/login", { email: "admin@eshop.com", password: "Admin123!" });
  if (!adm.json.token) { console.error("Admin login failed", adm); process.exit(1); }

  // import san pham
  const imp = await post("/api/admin/import-products", { products }, adm.json.token);
  console.log("Import products:", imp.status, imp.json.message);

  // dang ky users (bo qua neu da ton tai)
  let ok = 0, dup = 0;
  for (let i = 1; i <= N_USERS; i++) {
    const email = `perfuser${String(i).padStart(3, "0")}@eshop.test`;
    const r = await post("/api/register", { name: `Perf User ${i}`, email, password: PASSWORD });
    if (r.status === 200) ok++; else dup++;
  }
  console.log(`Registered users: ok=${ok} existed/err=${dup}`);

  // lay danh sach san pham that tu server de sinh CSV chinh xac
  const all = await (await fetch(BASE + "/api/products")).json();
  console.log("Total products on server:", all.length);

  const keywords = ["iPhone", "Samsung", "Xiaomi", "Oppo", "Laptop", "MacBook", "Dell",
    "Tai nghe", "Bàn phím", "Chuột", "Sạc", "Ốp lưng", "Cáp", "Đồng hồ", "Asus", "Lenovo", "Sony", "Razer"];

  // users.csv
  const usersCsv = ["email,password"];
  for (let i = 1; i <= N_USERS; i++)
    usersCsv.push(`perfuser${String(i).padStart(3, "0")}@eshop.test,${PASSWORD}`);
  fs.writeFileSync(path.join(dataDir, "users.csv"), usersCsv.join("\n") + "\n");

  // products.csv: keyword,product_id,product_name,price — lay ket qua dau tien tu server (giong $[0] cua JMeter)
  const prodCsv = ["keyword,product_id,product_name,price"];
  let ki = 0;
  for (let r = 0; r < 100; r++) {
    const kw = keywords[ki % keywords.length]; ki++;
    const matches = all.filter(p => p.name.includes(kw));
    if (matches.length === 0) { console.error("KEYWORD KHONG CO KET QUA:", kw); continue; }
    const first = matches[0];
    prodCsv.push(`${kw},${first.id},${first.name},${first.price}`);
  }
  fs.writeFileSync(path.join(dataDir, "products.csv"), prodCsv.join("\n") + "\n");
  console.log("CSV written: users.csv (", N_USERS, "rows ), products.csv (100 rows)");
  console.log("Sample products.csv rows:\n" + prodCsv.slice(1, 5).join("\n"));
}
main().catch(e => { console.error(e); process.exit(1); });
