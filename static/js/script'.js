/* ====================== 全局辅助函数 ====================== */

/**
 * 统一 API 请求封装，自动加 JSON 头、捕获异常
 * @param {string} path 请求路径，如 "/api/register"
 * @param {Object} opts fetch 配置
 * @returns {Promise<{ ok: boolean, status: number, data: any }>}
 */
async function apiFetch(path, opts = {}) {
  try {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json", ...opts.headers },
      ...opts
    });
    // 安全解析 JSON：若非 JSON（如 500 HTML 错误页），返回空对象而非崩溃
    const text = await res.text();
    let json;
    try {
      json = JSON.parse(text);
    } catch (e) {
      console.warn("⚠️ 非 JSON 响应:", text.substring(0, 200));
      json = { message: "服务器返回格式错误" };
    }
    return { ok: res.ok, status: res.status, data: json };
  } catch (e) {
    console.error("❌ apiFetch 网络异常:", e);
    return { ok: false, status: 0, data: { message: "网络连接失败，请检查服务是否启动" } };
  }
}

/**
 * 安全设置元素 innerText
 * @param {string} id 元素 ID
 * @param {string|number} value 文本内容
 */
function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.innerText = String(value);
}

/* ====================== 账号生成 ====================== */

/**
 * 根据角色生成唯一账号（Uxxx / Mxxx）
 * @param {string} role 'user' | 'merchant'
 * @returns {string}
 */
function generateAccount(role) {
  if (role === "admin") role = "user"; // 前端屏蔽 admin 注册
  const prefix = { user: "U", merchant: "M" }[role] || "U";
  return prefix + Date.now(); // 时间戳保证唯一性（简易版）
}

/* ====================== 用户流程 ====================== */

// ▼ 注册
async function register() {
  const role = document.getElementById("role")?.value || "user";
  if (role === "admin") return alert("前端禁止注册管理员账号！");    
  const email = document.getElementById("email")?.value.trim();
  const phone = document.getElementById("phone")?.value.trim();
  const pwd = document.getElementById("password")?.value.trim();

  // ✅ 新增：空值 + 格式双重校验
  if (!email || !phone || !pwd) return alert("请填写完整信息！");

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  if (!emailRegex.test(email)) {
    return alert("📧 邮箱格式不正确，请检查（例如：user@example.com）");
  }

  const phoneRegex = /^1[3-9]\d{9}$/;
  if (!phoneRegex.test(phone)) {
    return alert("📱 手机号应为 11 位中国大陆号码（如：13812345678）");
  }

  // ✅ 密码长度校验（至少 6 位，建议 8~20）
  if (pwd.length < 6) {
    return alert("🔒 密码至少 6 位，请重新设置");
  }
  if (pwd.length > 20) {
    return alert("🔒 密码长度不能超过 20 位");
  }

  const id = generateAccount(role);
  const idEl = document.getElementById("generatedId");
  if (idEl) idEl.innerText = id;

  const res = await apiFetch("/api/register", {
    method: "POST",
    body: JSON.stringify({ role, id, email, phone, password: pwd })
  });

  // ✅ 优先显示后端错误信息，fallback 到通用提示
  const msg = res.data?.message || (res.ok ? "注册成功" : "注册失败，请重试");
  alert(msg);
  if (res.ok) window.location.href = "index.html";
}

// ▼ 登录 + 记住账号
async function login() {
  const id = document.getElementById("login_id")?.value.trim();
  const pwd = document.getElementById("login_password")?.value.trim();
  if (!id || !pwd) return alert("⚠️ 请填写账号和密码！");

  const res = await apiFetch("/api/l", {
    method: "POST",
    body: JSON.stringify({ id, password: pwd })
  });

  if (!res.ok) {
    const msg = res.data?.message || "登录失败";
    return alert("❌ " + msg);
  }

  // 记住账号：localStorage
  const remember = document.getElementById("rememberMe");
  if (remember?.checked) {
    localStorage.setItem("remember_id", id);
  } else {
    localStorage.removeItem("remember_id");
  }

  // 跳转首页（按角色）
  const role = res.data.role || "user";
  if (role === "user") window.location.href = "products.html";
  else if (role === "merchant") window.location.href = "merchant.html";
  else if (role === "admin") window.location.href = "admin.html";
}

// ▼ 初始化登录页（回填记住的账号）
function initLoginPage() {
  const saved = localStorage.getItem("remember_id");
  if (saved) {
    const el = document.getElementById("login_id");
    const chk = document.getElementById("rememberMe");
    if (el) el.value = saved;
    if (chk) chk.checked = true;
  }
}

/* ====================== 密码找回流程 ====================== */

let _countdown = 60; // 全局倒计时（⚠️ 有竞态风险，生产环境建议绑定到按钮实例）

async function sendCode() {
  const id = document.getElementById("fp_id")?.value.trim();
  const email = document.getElementById("fp_email")?.value.trim();
  if (!id || !email) return alert("⚠️ 请填写账号与邮箱！");

  const btn = document.getElementById("sendCodeBtn");
  if (!btn) return;

  // 防重复点击
  if (btn.disabled) return;

  btn.disabled = true;
  let cd = _countdown;
  btn.innerText = `${cd} 秒`;

  const timer = setInterval(() => {
    cd--;
    btn.innerText = `${cd} 秒`;
    if (cd <= 0) {
      clearInterval(timer);
      btn.disabled = false;
      btn.innerText = "发送验证码";
    }
  }, 1000);

  const res = await apiFetch("/api/send-reset-code", {
    method: "POST",
    body: JSON.stringify({ id, email })
  });

  const msg = res.data?.message || (res.ok ? "✅ 验证码已发送" : "❌ 发送失败");
  alert(msg);
  if (!res.ok) {
    // 发送失败则提前重置按钮
    clearInterval(timer);
    btn.disabled = false;
    btn.innerText = "发送验证码";
  }
}

// ▼ 重设密码
async function resetPassword() {
  const id = document.getElementById("rp_id")?.value.trim();
  const code = document.getElementById("rp_code")?.value.trim();
  const pwd = document.getElementById("rp_newpwd")?.value.trim();

  if (!id || !code || !pwd) return alert("⚠️ 请填写完整信息！");

  const res = await apiFetch("/api/reset-password", {
    method: "POST",
    body: JSON.stringify({ id, code, password: pwd })
  });

  const msg = res.data?.message || (res.ok ? "✅ 重设成功" : "❌ 重设失败");
  alert(msg);
  if (res.ok) window.location.href = "index.html";
}

/* ====================== 用户端：商品 & 出行 ====================== */

async function initProductsPage() {
  fetchProducts();
}

async function fetchProducts() {
  const res = await apiFetch("/api/products");
  const container = document.getElementById("productList");
  if (!container) return;

  container.innerHTML = "";
  const products = (res.ok && Array.isArray(res.data.products)) ? res.data.products : [];

  if (products.length === 0) {
    container.innerHTML = `<div class="empty-state">🛒 暂无商品，敬请期待</div>`;
    return;
  }

  products.forEach(p => {
    const d = document.createElement("div");
    d.className = "product-card";
    d.innerHTML = `
      <div>
        <h4 style="margin:0">${escapeHtml(p.name)}</h4>
        <p style="color:#6b7280;margin:6px 0">${escapeHtml(p.desc || "")}</p>
        <div style="margin-top:8px">
          <span class="tag green">${p.points} 积分</span>
          <span style="margin-left:12px;color:#2d4ddb;font-weight:700">¥${(p.price || 0).toFixed(2)}</span>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:8px;">
        <button class="btn" onclick="redeemProduct('${p.id}')">🎁 兑换</button>
      </div>
    `;
    container.appendChild(d);
  });
}

// ▼ XSS 防护：转义用户输入
function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "<")
    .replace(/>/g, ">")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ▼ 兑换商品
async function redeemProduct(prodId) {
  const addr = prompt("📦 请输入收货地址（例：张三 138****1234 北京市海淀区XX路）");
  if (!addr) return alert("⚠️ 地址不能为空");

  const res = await apiFetch("/api/orders", {
    method: "POST",
    body: JSON.stringify({ productId: prodId, address: addr })
  });

  const msg = res.data?.message || (res.ok ? "✅ 下单成功！" : "❌ 兑换失败");
  alert(msg);
  if (res.ok) fetchProducts(); // 刷新列表
}

// ▼ 用户提交出行（需补充：你未提供 submitTrip，此处补全）
async function submitTrip() {
  const period = document.getElementById("trip_period")?.value.trim();
  const mode = document.getElementById("trip_mode")?.value;
  const distance = parseFloat(document.getElementById("trip_distance")?.value);
  const note = document.getElementById("trip_note")?.value.trim();

  if (!period || isNaN(distance) || distance <= 0) {
    return alert("⚠️ 请填写完整且有效的出行信息！");
  }

  const res = await apiFetch("/api/trips", {
    method: "POST",
    body: JSON.stringify({ period, mode, distance, note })
  });

  const msg = res.data?.message || (res.ok ? "✅ 提交成功，等待审核" : "❌ 提交失败");
  alert(msg);
  if (res.ok) {
    // 清空表单（可选）
    document.getElementById("trip_form")?.reset();
  }
}

function initUserTripPage() {
  // 可选：预填本周日期
  const today = new Date();
  const weekAgo = new Date(today);
  weekAgo.setDate(today.getDate() - 6);
  const fmt = d => d.toISOString().slice(0, 10);
  const el = document.getElementById("trip_period");
  if (el && !el.value) {
    el.value = `${fmt(weekAgo)} ~ ${fmt(today)}`;
  }
}

/* ====================== 商户端 ====================== */

async function initMerchantDashboard() {
  fetchMerchantProducts();
  fetchMerchantOrders();
  fetchMerchantWithdrawals();
}

async function createMerchantProduct() {
  const name = document.getElementById("mp_name")?.value.trim();
  const price = parseFloat(document.getElementById("mp_price")?.value);
  const points = parseInt(document.getElementById("mp_points")?.value, 10);
  const desc = document.getElementById("mp_desc")?.value.trim();

  if (!name || isNaN(price) || price <= 0 || isNaN(points) || points <= 0) {
    return alert("⚠️ 请填写完整且有效的商品信息！");
  }

  const res = await apiFetch("/api/merchant/products", {
    method: "POST",
    body: JSON.stringify({ name, price, points, desc })
  });

  const msg = res.data?.message || (res.ok ? "✅ 上架成功" : "❌ 上架失败");
  alert(msg);
  if (res.ok) {
    document.getElementById("mp_form")?.reset();
    fetchMerchantProducts();
  }
}

async function fetchMerchantProducts() {
  const res = await apiFetch("/api/merchant/products");
  const el = document.getElementById("merchantProductList");
  if (!el) return;

  el.innerHTML = "";
  const list = (res.ok && Array.isArray(res.data.products)) ? res.data.products : [];

  if (typeof res.data?.availablePoints === "number") {
    setText("merchantMetricPoints", res.data.availablePoints);
  }
  setText("merchantMetricProducts", list.length);

  if (list.length === 0) {
    el.innerHTML = `<div class="empty-state">📭 暂无商品</div>`;
    return;
  }

  list.forEach(p => {
    const div = document.createElement("div");
    div.className = "product-card";
    div.innerHTML = `
      <div>
        <h4 style="margin:0">${escapeHtml(p.name)}</h4>
        <p style="color:#6b7280;margin:6px 0">¥${(p.price || 0).toFixed(2)} · ${p.points} 积分</p>
      </div>
      <div style="display:flex;flex-direction:column;gap:8px">
        <button class="btn-ghost" onclick="merchantEditProduct('${p.id}')">✏️ 编辑</button>
        <button class="btn" onclick="merchantDeleteProduct('${p.id}')">🗑️ 下架</button>
      </div>`;
    el.appendChild(div);
  });
}

function merchantEditProduct(id) {
  alert(`🔧 编辑商品（ID: ${id}）—— 功能待实现`);
}

async function merchantDeleteProduct(id) {
  if (!confirm("⚠️ 确认下架该商品？此操作不可逆")) return;

  const res = await apiFetch(`/api/merchant/products/${id}`, { method: "DELETE" });
  const msg = res.data?.message || (res.ok ? "✅ 下架成功" : "❌ 下架失败");
  alert(msg);
  if (res.ok) fetchMerchantProducts();
}

async function fetchMerchantOrders() {
  const res = await apiFetch("/api/merchant/orders");
  const el = document.getElementById("merchantOrderList");
  if (!el) return;

  el.innerHTML = "";
  const orders = (res.ok && Array.isArray(res.data.orders)) ? res.data.orders : [];
  setText("merchantMetricOrders", orders.length);

  if (orders.length === 0) {
    el.innerHTML = `<div class="empty-state">📭 暂无订单</div>`;
    return;
  }

  orders.forEach(o => {
    const node = document.createElement("div");
    node.className = "card";
    node.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <p style="margin:0"><strong>📦 订单：</strong>${escapeHtml(o.id)}</p>
          <p style="color:#6b7280;margin:6px 0">${escapeHtml(o.productName)} · ${escapeHtml(o.address)}</p>
        </div>
        <div>
          <div class="tag ${o.status === 'PAID' ? 'green' : 'orange'}">${o.status}</div>
          ${o.status === 'PAID' ? `<div style="margin-top:8px"><button class="btn" onclick="merchantMarkShipped('${o.id}')">🚚 标发货</button></div>` : ''}
        </div>
      </div>`;
    el.appendChild(node);
  });
}

async function merchantMarkShipped(id) {
  if (!confirm("📦 确认已发货？用户将收到通知")) return;

  const res = await apiFetch(`/api/merchant/orders/${id}/ship`, { method: "POST" });
  const msg = res.data?.message || (res.ok ? "✅ 已标记发货" : "❌ 操作失败");
  alert(msg);
  if (res.ok) fetchMerchantOrders();
}

async function fetchMerchantWithdrawals() {
  const res = await apiFetch("/api/merchant/withdrawals");
  const el = document.getElementById("merchantWithdrawalList");
  if (!el) return;

  el.innerHTML = "";
  const items = (res.ok && Array.isArray(res.data.items)) ? res.data.items : [];
  items.forEach(i => {
    const d = document.createElement("div");
    d.className = "card";
    d.innerHTML = `
      <div style="display:flex;justify-content:space-between">
        <div>💰 申请：¥${i.amount?.toFixed(2) || 0} · <span class="tag ${i.status === 'APPROVED' ? 'green' : i.status === 'REJECTED' ? 'orange' : ''}">${i.status || 'PENDING'}</span></div>
        <div>${new Date(i.createdAt).toLocaleString()}</div>
      </div>`;
    el.appendChild(d);
  });
}

/* ====================== 管理员端 ====================== */

async function initAdminReview() {
  fetchPendingTrips();
  fetchWithdrawalRequests();
  fetchPointRecords();
}

async function fetchPendingTrips() {
  const res = await apiFetch("/api/admin/trips/pending");
  const el = document.getElementById("pendingTrips");
  if (!el) return;

  el.innerHTML = "";
  const items = (res.ok && Array.isArray(res.data.trips)) ? res.data.trips : [];
  setText("metricPendingTrips", items.length);

  if (items.length === 0) {
    el.innerHTML = `<div class="empty-state">✅ 暂无待审出行</div>`;
    return;
  }

  items.forEach(t => {
    const node = document.createElement("div");
    node.className = "card";
    node.innerHTML = `
      <div style="display:flex;justify-content:space-between">
        <div>
          <p style="margin:0"><strong>👤 ${escapeHtml(t.userId || t.userName)}</strong></p>
          <p style="color:#6b7280;margin-top:6px">${t.mode} · ${t.distance} km</p>
        </div>
        <div>
          <button class="btn" onclick="adminDecideTrip('${t.id}', true)">✅ 通过</button>
          <button class="btn-ghost" style="margin-left:8px" onclick="adminDecideTrip('${t.id}', false)">❌ 驳回</button>
        </div>
      </div>`;
    el.appendChild(node);
  });
}

async function adminDecideTrip(id, approve) {
  const msg = approve ? "✅ 通过并发放积分？" : "❌ 确认驳回？";
  if (!confirm(msg)) return;

  const res = await apiFetch(`/api/admin/trips/${id}/decide`, {
    method: "POST",
    body: JSON.stringify({ approve })
  });

  const text = res.data?.message || (res.ok ? "✅ 操作成功" : "❌ 操作失败");
  alert(text);
  if (res.ok) fetchPendingTrips();
}

async function fetchWithdrawalRequests() {
  const res = await apiFetch("/api/admin/withdrawals/pending");
  const el = document.getElementById("withdrawalRequests");
  if (!el) return;

  el.innerHTML = "";
  const items = (res.ok && Array.isArray(res.data.items)) ? res.data.items : [];
  setText("metricWithdrawals", items.length);

  if (items.length === 0) {
    el.innerHTML = `<div class="empty-state">✅ 暂无提现申请</div>`;
    return;
  }

  items.forEach(w => {
    const node = document.createElement("div");
    node.className = "card";
    node.innerHTML = `
      <div style="display:flex;justify-content:space-between">
        <div>
          <p style="margin:0"><strong>🏪 ${escapeHtml(w.merchantId)}</strong></p>
          <p style="color:#6b7280;margin-top:6px">💰 ¥${w.amount?.toFixed(2) || 0}</p>
        </div>
        <div>
          <button class="btn" onclick="adminDecideWithdrawal('${w.id}', true)">✅ 批准</button>
          <button class="btn-ghost" style="margin-left:8px" onclick="adminDecideWithdrawal('${w.id}', false)">❌ 拒绝</button>
        </div>
      </div>`;
    el.appendChild(node);
  });
}

async function adminDecideWithdrawal(id, approve) {
  const msg = approve ? "✅ 确认批准提现？资金将划转" : "❌ 确认拒绝提现？";
  if (!confirm(msg)) return;

  const res = await apiFetch(`/api/admin/withdrawals/${id}/decide`, {
    method: "POST",
    body: JSON.stringify({ approve })
  });

  const text = res.data?.message || (res.ok ? "✅ 操作成功" : "❌ 操作失败");
  alert(text);
  if (res.ok) fetchWithdrawalRequests();
}

async function fetchPointRecords() {
  const res = await apiFetch("/api/points/records");
  const el = document.getElementById("pointRecords");
  if (!el) return;

  el.innerHTML = "";
  const items = (res.ok && Array.isArray(res.data.items)) ? res.data.items : [];
  const totalPoints = items.reduce((sum, r) => sum + (Number(r.points) || 0), 0);
  setText("metricPoints", items.length ? `${totalPoints > 0 ? '+' : ''}${totalPoints}` : "0");

  if (items.length === 0) {
    el.innerHTML = `<div class="empty-state">📊 暂无积分记录</div>`;
    return;
  }

  items.forEach(r => {
    const node = document.createElement("div");
    node.className = "list-row";
    node.style.display = "flex";
    node.style.justifyContent = "space-between";
    node.innerHTML = `
      <div>${new Date(r.time).toLocaleString()} · ${r.type}</div>
      <div><strong>${r.points > 0 ? '+' : ''}${r.points}</strong></div>`;
    el.appendChild(node);
  });
}

/* ====================== 全局暴露（供 HTML onclick 调用） ====================== */

// 用户流程
window.register = register;
window.login = login;
window.initLoginPage = initLoginPage;
window.sendCode = sendCode;
window.resetPassword = resetPassword;

// 用户端
window.initProductsPage = initProductsPage;
window.fetchProducts = fetchProducts;
window.redeemProduct = redeemProduct;
window.submitTrip = submitTrip;          // ← 新增补全
window.initUserTripPage = initUserTripPage;

// 商户端
window.initMerchantDashboard = initMerchantDashboard;
window.createMerchantProduct = createMerchantProduct;
window.fetchMerchantProducts = fetchMerchantProducts;
window.merchantEditProduct = merchantEditProduct;
window.merchantDeleteProduct = merchantDeleteProduct;
window.fetchMerchantOrders = fetchMerchantOrders;
window.merchantMarkShipped = merchantMarkShipped;
window.fetchMerchantWithdrawals = fetchMerchantWithdrawals;

// 管理员端
window.initAdminReview = initAdminReview;
window.fetchPendingTrips = fetchPendingTrips;
window.adminDecideTrip = adminDecideTrip;
window.fetchWithdrawalRequests = fetchWithdrawalRequests;
window.adminDecideWithdrawal = adminDecideWithdrawal;
window.fetchPointRecords = fetchPointRecords;
