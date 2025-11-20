/* 辅助函数 */
async function apiFetch(path, opts = {}) {
  try {
    const res = await fetch(path, Object.assign({
      headers: Object.assign({ "Content-Type": "application/json" }, opts.headers || {})
    }, opts));
    const json = await res.json().catch(()=>({}));
    return { ok: res.ok, status: res.status, data: json };
  } catch (e) {
    console.error("apiFetch error", e);
    return { ok:false, status:0, data:{ message:"网络错误" } };
  }
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.innerText = value;
}

/* 自动生成账号 */
function generateAccount(role) {
  if (role === "admin") role = "user";
  const prefix = { user: "U", merchant: "M" }[role] || "U";
  return prefix + Date.now();
}

/* 注册 */
async function register() {
  const role = document.getElementById("role")?.value || "user";
  if (role === "admin") return alert("前端禁止注册管理员账号！");    
  const email = document.getElementById("email")?.value.trim();
  const phone = document.getElementById("phone")?.value.trim();
  const pwd = document.getElementById("password")?.value.trim();
  if (!email || !phone || !pwd) return alert("请填写完整信息！");
  const id = generateAccount(role);
  document.getElementById("generatedId") && (document.getElementById("generatedId").innerText = id);
  const res = await apiFetch("/api/register", { method: "POST", body: JSON.stringify({ role, id, email, phone, password: pwd })});
  alert(res.data?.message || (res.ok ? "注册成功" : "注册失败"));  
  if (res.ok) window.location.href = "index.html";
}

/* 登录 + 记住账号 */
async function login() {
  const id = document.getElementById("login_id")?.value.trim();
  const pwd = document.getElementById("login_password")?.value.trim();
  if (!id || !pwd) return alert("请填写账号和密码！");
  const res = await apiFetch("/api/login", { method: "POST", body: JSON.stringify({ id, password: pwd })});
  if (!res.ok) return alert(res.data?.message || "登录失败");
  // 记住账号
  const remember = document.getElementById("rememberMe");
  if (remember && remember.checked) localStorage.setItem("remember_id", id);
  else localStorage.removeItem("remember_id");
  const role = res.data.role || "user";
  if (role === "user") window.location.href = "products.html";
  else if (role === "merchant") window.location.href = "merchant.html";
  else if (role === "admin") window.location.href = "admin.html";
}

function initLoginPage() {
  const saved = localStorage.getItem("remember_id");
  if (saved) {
    const el = document.getElementById("login_id"); if (el) el.value = saved;
    const chk = document.getElementById("rememberMe"); if (chk) chk.checked = true;
  }
}

/* 忘记密码，发送验证码*/
let _countdown = 60;
async function sendCode() {
  const id = document.getElementById("fp_id")?.value.trim();
  const email = document.getElementById("fp_email")?.value.trim();
  if (!id || !email) return alert("请填写账号与邮箱！");
  const btn = document.getElementById("sendCodeBtn");
  btn.disabled = true;
  btn.innerText = `${_countdown} 秒`;
  const timer = setInterval(()=> {
    _countdown--;
    btn.innerText = `${_countdown} 秒`;
    if (_countdown <= 0) { clearInterval(timer); btn.disabled=false; btn.innerText="发送验证码"; _countdown=60; }
  },1000);
  const res = await apiFetch("/api/send-reset-code", { method: "POST", body: JSON.stringify({ id, email })});
  alert(res.data?.message || (res.ok ? "验证码已发送" : "发送失败"));
}

/* 重设密码*/
async function resetPassword() {
  const id = document.getElementById("rp_id")?.value.trim();
  const code = document.getElementById("rp_code")?.value.trim();
  const pwd = document.getElementById("rp_newpwd")?.value.trim();
  if (!id || !code || !pwd) return alert("请填写完整信息！");
  const res = await apiFetch("/api/reset-password", { method: "POST", body: JSON.stringify({ id, code, password: pwd }) });
  alert(res.data?.message || (res.ok ? "重设成功" : "重设失败"));
  if (res.ok) window.location.href = "index.html";
}

/* (用户浏览商品并兑换)*/
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
    container.innerHTML = `<div class="empty-state">暂无商品，敬请期待</div>`; return;
  }
  products.forEach(p => {
    const d = document.createElement("div");
    d.className = "product-card";
    d.innerHTML = `
      <div>
        <h4 style="margin:0">${p.name}</h4>
        <p style="color:#6b7280;margin:6px 0">${p.desc || ""}</p>
        <div style="margin-top:8px">
          <span class="tag green">${p.points} 积分</span>
          <span style="margin-left:12px;color:#2d4ddb;font-weight:700">¥${(p.price||0).toFixed(2)}</span>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:8px;">
        <button class="btn" onclick="redeemProduct('${p.id}')">兑换</button>
      </div>
    `;
    container.appendChild(d);
  });
}

/* 兑换商品 */
async function redeemProduct(prodId) {
  const addr = prompt("请输入收货地址（示例：张三 / 电话 / 详细地址）");
  if (!addr) return alert("请填写地址");
  const res = await apiFetch("/api/orders", { method: "POST", body: JSON.stringify({ productId: prodId, address: addr })});
  alert(res.data?.message || (res.ok ? "下单成功" : "兑换失败"));
  if (res.ok) fetchProducts();
}

/* 商户控制台 (上架/订单/提现) */
async function initMerchantDashboard() {
  fetchMerchantProducts();
  fetchMerchantOrders();
  fetchMerchantWithdrawals();
}
async function createMerchantProduct() {
  const name = document.getElementById("mp_name")?.value.trim();
  const price = parseFloat(document.getElementById("mp_price")?.value);
  const points = parseInt(document.getElementById("mp_points")?.value,10);
  const desc = document.getElementById("mp_desc")?.value.trim();
  if (!name || isNaN(price) || isNaN(points)) return alert("请填写完整商品信息！");
  const res = await apiFetch("/api/merchant/products", { method: "POST", body: JSON.stringify({ name, price, points, desc })});
  alert(res.data?.message || (res.ok ? "上架成功" : "上架失败"));
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
  if (typeof res.data?.availablePoints === "number") setText("merchantMetricPoints", res.data.availablePoints);
  setText("merchantMetricProducts", list.length);
  if (list.length === 0) { el.innerHTML = "<div class='empty-state'>暂无商品</div>"; return; }
  list.forEach(p => {
    const div = document.createElement("div");
    div.className = "product-card";
    div.innerHTML = `<div>
      <h4 style="margin:0">${p.name}</h4>
      <p style="color:#6b7280;margin:6px 0">¥${(p.price||0).toFixed(2)} · ${p.points} 积分</p>
    </div>
    <div style="display:flex;flex-direction:column;gap:8px">
      <button class="btn-ghost" onclick="merchantEditProduct('${p.id}')">编辑</button>
      <button class="btn" onclick="merchantDeleteProduct('${p.id}')">下架</button>
    </div>`;
    el.appendChild(div);
  });
}
function merchantEditProduct(id){ alert("编辑功能（占位）"); }
async function merchantDeleteProduct(id){
  if (!confirm("确认下架该商品？")) return;
  const res = await apiFetch(`/api/merchant/products/${id}`, { method: "DELETE" });
  alert(res.data?.message || (res.ok ? "下架成功" : "下架失败"));
  if (res.ok) fetchMerchantProducts();
}
async function fetchMerchantOrders() {
  const res = await apiFetch("/api/merchant/orders");
  const el = document.getElementById("merchantOrderList");
  if (!el) return;
  el.innerHTML = "";
  const orders = (res.ok && Array.isArray(res.data.orders)) ? res.data.orders : [];
  setText("merchantMetricOrders", orders.length);
  if (orders.length === 0) { el.innerHTML = "<div class='empty-state'>暂无订单</div>"; return; }
  orders.forEach(o => {
    const node = document.createElement("div");
    node.className = "card";
    node.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center">
      <div><p style="margin:0"><strong>订单：</strong>${o.id}</p><p style="color:#6b7280;margin:6px 0">${o.productName} · ${o.address}</p></div>
      <div><div class="tag ${o.status==='PAID'?'green':'orange'}">${o.status}</div>
      ${o.status==='PAID'?`<div style="margin-top:8px"><button class="btn" onclick="merchantMarkShipped('${o.id}')">标发货</button></div>`:''}
      </div>
    </div>`;
    el.appendChild(node);
  });
}
async function merchantMarkShipped(id) {
  if (!confirm("确认标记已发货？")) return;
  const res = await apiFetch(`/api/merchant/orders/${id}/ship`, { method: "POST" });
  alert(res.data?.message || (res.ok ? "已标记" : "操作失败"));
  if (res.ok) fetchMerchantOrders();
}
async function merchantRequestWithdrawal(amount, bankInfo) {
  const res = await apiFetch("/api/merchant/withdrawals", { method: "POST", body: JSON.stringify({ amount, bankInfo })});
  alert(res.data?.message || (res.ok ? "申请已提交" : "申请失败"));
  if (res.ok) fetchMerchantWithdrawals();
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
    d.innerHTML = `<div style="display:flex;justify-content:space-between"><div>申请：¥${i.amount.toFixed(2)} · ${i.status}</div><div>${new Date(i.createdAt).toLocaleString()}</div></div>`;
    el.appendChild(d);
  });
}

/* 管理员审核*/
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
  if (items.length === 0) { el.innerHTML = "<div class='empty-state'>暂无待审。</div>"; return; }
  items.forEach(t => {
    const node = document.createElement("div");
    node.className = "card";
    node.innerHTML = `<div style="display:flex;justify-content:space-between">
      <div><p style="margin:0"><strong>${t.userId || t.userName}</strong></p><p style="color:#6b7280;margin-top:6px">${t.mode} · ${t.distance} km</p></div>
      <div><button class="btn" onclick="adminDecideTrip('${t.id}', true)">通过</button><button class="btn-ghost" style="margin-left:8px" onclick="adminDecideTrip('${t.id}', false)">驳回</button></div>
    </div>`;
    el.appendChild(node);
  });
}
async function adminDecideTrip(id, approve) {
  if (!confirm(approve ? "确认通过并发放积分？" : "确认驳回？")) return;
  const res = await apiFetch(`/api/admin/trips/${id}/decide`, { method: "POST", body: JSON.stringify({ approve })});
  alert(res.data?.message || (res.ok ? "操作成功" : "操作失败"));
  if (res.ok) fetchPendingTrips();
}
async function fetchWithdrawalRequests() {
  const res = await apiFetch("/api/admin/withdrawals/pending");
  const el = document.getElementById("withdrawalRequests");
  if (!el) return;
  el.innerHTML = "";
  const items = (res.ok && Array.isArray(res.data.items)) ? res.data.items : [];
  setText("metricWithdrawals", items.length);
  if (items.length === 0) { el.innerHTML = "<div class='empty-state'>暂无提现申请</div>"; return; }
  items.forEach(w => {
    const node = document.createElement("div");
    node.className = "card";
    node.innerHTML = `<div style="display:flex;justify-content:space-between"><div><p style="margin:0"><strong>${w.merchantId}</strong></p><p style="color:#6b7280;margin-top:6px">¥${w.amount.toFixed(2)}</p></div><div><button class="btn" onclick="adminDecideWithdrawal('${w.id}', true)">批准</button><button class="btn-ghost" style="margin-left:8px" onclick="adminDecideWithdrawal('${w.id}', false)">拒绝</button></div></div>`;
    el.appendChild(node);
  });
}
async function adminDecideWithdrawal(id, approve) {
  if (!confirm(approve ? "批准提现？" : "拒绝提现？")) return;
  const res = await apiFetch(`/api/admin/withdrawals/${id}/decide`, { method: "POST", body: JSON.stringify({ approve })});
  alert(res.data?.message || (res.ok ? "操作成功" : "操作失败"));
  if (res.ok) fetchWithdrawalRequests();
}
async function fetchPointRecords() {
  const res = await apiFetch("/api/points/records");
  const el = document.getElementById("pointRecords");
  if (!el) return;
  el.innerHTML = "";
  const items = (res.ok && Array.isArray(res.data.items)) ? res.data.items : [];
  const totalPoints = items.reduce((sum, r) => sum + (Number(r.points) || 0), 0);
  setText("metricPoints", items.length ? `${totalPoints > 0 ? "+" : ""}${totalPoints}` : "0");
  if (items.length === 0) { el.innerHTML = "<div class='empty-state'>暂无记录</div>"; return; }
  items.forEach(r => {
    const node = document.createElement("div");
    node.className = "list-row";
    node.innerHTML = `<div>${new Date(r.time).toLocaleString()} · ${r.type}</div><div><strong>${r.points>0?'+':''}${r.points}</strong></div>`;
    el.appendChild(node);
  });
}

/*全局作用域*/
window.initProductsPage = initProductsPage;
window.initMerchantDashboard = initMerchantDashboard;
window.initAdminReview = initAdminReview;
window.register = register;
window.login = login;
window.initLoginPage = initLoginPage;
window.sendCode = sendCode;
window.resetPassword = resetPassword;
window.createMerchantProduct = createMerchantProduct;
window.fetchMerchantProducts = fetchMerchantProducts;
window.createMerchantProduct = createMerchantProduct;
window.fetchMerchantOrders = fetchMerchantOrders;
window.merchantMarkShipped = merchantMarkShipped;
window.merchantRequestWithdrawal = merchantRequestWithdrawal;
window.redeemProduct = redeemProduct;
window.fetchProducts = fetchProducts;
window.fetchPointRecords = fetchPointRecords;
