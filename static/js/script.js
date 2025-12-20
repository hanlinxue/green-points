// 直接执行脚本

function generateAccount(role) {
  if (role === "admin") role = "user";
  const prefix = { user: "U", merchant: "M" }[role] || "U";
  return prefix + Date.now();
}
/* apiFetch函数 */
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

/* 注册 */
async function register()  {
  const role = document.getElementById("role")?.value || "user";
  if (role === "admin") return alert("前端禁止注册管理员账号！");    
  const email = document.getElementById("email")?.value.trim();
  const phone = document.getElementById("phone")?.value.trim();
  const pwd = document.getElementById("password")?.value.trim();
  if (!email || !phone || !pwd) return alert("请填写完整信息！");
  const id = generateAccount(role);
  document.getElementById("generatedId") && (document.getElementById("generatedId").innerText = id);
  const res = await apiFetch("/user/register", { method: "POST", body: JSON.stringify({ role, id, email, phone, password: pwd })});
  alert(res.data?.message || (res.ok ? "注册成功,即将返回登录页面!" : "注册失败"));
  if (res.ok) window.location.href = "/user";
}

/* 登录 + 记住账号 */
async function login() {
  const id = document.getElementById("login_id")?.value.trim();
  const pwd = document.getElementById("login_password")?.value.trim();
  if (!id || !pwd) return alert("请填写账号和密码！");
  const res = await apiFetch("/user/login", { method: "POST", body: JSON.stringify({ id, password: pwd })});
  console.log("login response:", res);  // ← 调试关键
  if (!res.ok) return alert(res.data?.message || "登录失败");
  // 记住账号
  const remember = document.getElementById("rememberMe");
  if (remember && remember.checked) localStorage.setItem("remember_id", id);
  else localStorage.removeItem("remember_id");
  const role = res.data.role || "user";
  if (role === "user") window.location.href = "/user/user_index";
  else if (role === "merchant") window.location.href = "/merchant/merchant_product";
  else if (role === "admin") window.location.href = "/admin/admin_index";
}

function initLoginPage() {
  const saved = localStorage.getItem("remember_id");
  if (saved) {
    const el = document.getElementById("login_id"); if (el) el.value = saved;
    const chk = document.getElementById("rememberMe"); if (chk) chk.checked = true;
  }
}

/* 忘记密码，发送验证码*/
var _countdown = 60;
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

/* 跳转到重设密码页（传递账号/邮箱/验证码） */
function toResetPage() {
  const id = document.getElementById("fp_id")?.value.trim();
  const email = document.getElementById("fp_email")?.value.trim();
  const code = document.getElementById("fp_code")?.value.trim();
  if (!id || !email) return alert("请填写账号与邮箱！");
  if (!code) return alert("请输入验证码！");
  window.location.href = `/user/reset?id=${encodeURIComponent(id)}&email=${encodeURIComponent(email)}&code=${encodeURIComponent(code)}`;
}


/* 重设密码*/
async function resetPassword() {
  // 1. 读取URL中传递的账号/邮箱/验证码（核心修改）
  const urlParams = new URLSearchParams(window.location.search);
  const id = urlParams.get("id");
  const email = urlParams.get("email");
  const code = urlParams.get("code");

  // 2. 获取新密码和确认新密码（核心修改）
  const pwd = document.getElementById("rp_newpwd")?.value.trim();
  const confirmPwd = document.getElementById("rp_confirm_pwd")?.value.trim();
  
  // 3. 校验逻辑（核心修改）
  if (!pwd || !confirmPwd) return alert("请填写新密码和确认密码！");
  if (pwd !== confirmPwd) return alert("两次输入的密码不一致！");
  if (!id || !code) return alert("验证信息缺失，请返回上一页重新操作！");

  // 4. 调用重置密码API（补充email参数）
  const res = await apiFetch("/api/reset-password", {
    method: "POST", 
    body: JSON.stringify({ id, email, code, password: pwd }) 
  });
  alert(res.data?.message || (res.ok ? "重设成功" : "重设失败"));
  if (res.ok) window.location.href = "index.html";
}

/*用户浏览商品并兑换页面刷新*/
async function initProductsPage() {
  await fetchProducts();
}
async function fetchProducts() {
  const res = await apiFetch("/user_index");
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
  // 先尝试获取用户地址列表
  try {
    const addrResponse = await fetch('/user/api/addresses');
    let addr = null;

    if (addrResponse.ok) {
      const addresses = await addrResponse.json();

      if (addresses && addresses.length > 0) {
        // 显示地址选择界面
        let addrHtml = '<div style="padding: 20px; background: #f5f5f5; border-radius: 8px; max-width: 600px;">';
        addrHtml += '<h3 style="margin-top: 0; color: #333;">请选择收货地址：</h3>';
        addrHtml += '<div id="addrList"></div>';
        addrHtml += '<button id="confirmAddr" style="margin-top: 15px; padding: 8px 20px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer;">确认选择</button>';
        addrHtml += '<button id="cancelAddr" style="margin-left: 10px; padding: 8px 20px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">取消</button>';
        addrHtml += '</div>';

        // 创建模态框
        const modal = document.createElement('div');
        modal.id = 'addrModal';
        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 10000;';
        modal.innerHTML = addrHtml;
        document.body.appendChild(modal);

        // 渲染地址列表
        const addrList = modal.querySelector('#addrList');
        let selectedAddrId = null;

        addresses.forEach((addr, index) => {
          const addrDiv = document.createElement('div');
          addrDiv.style.cssText = 'background: white; padding: 12px; margin: 8px 0; border-radius: 4px; cursor: pointer; border: 2px solid transparent;';
          addrDiv.dataset.addrId = addr.id;

          addrDiv.innerHTML = `
            <input type="radio" name="address" value="${addr.id}" id="addr_${index}" style="margin-right: 10px;">
            <label for="addr_${index}" style="cursor: pointer;">
              <strong>${addr.name}</strong> ${addr.phone} ${addr.is_default ? '<span style="color: #28a745;">[默认]</span>' : ''}<br>
              <span style="color: #666; font-size: 14px;">${addr.region} ${addr.detail}</span>
            </label>
          `;

          addrDiv.addEventListener('click', function() {
            document.querySelectorAll('#addrList > div').forEach(d => d.style.borderColor = 'transparent');
            this.style.borderColor = '#28a745';
            this.querySelector('input').checked = true;
            selectedAddrId = addr.id;
          });

          addrList.appendChild(addrDiv);
        });

        // 绑定确认按钮
        modal.querySelector('#confirmAddr').onclick = async function() {
          if (!selectedAddrId) {
            alert('请选择一个地址');
            return;
          }

          const selectedAddr = addresses.find(a => a.id == selectedAddrId);
          addr = `${selectedAddr.name} / ${selectedAddr.phone} / ${selectedAddr.region} ${selectedAddr.detail}`;

          document.body.removeChild(modal);

          // 调用兑换API
          const res = await apiFetch("/user/api/orders", { method: "POST", body: JSON.stringify({ productId: prodId, address: addr })});
          alert(res.data?.message || (res.ok ? "下单成功" : "兑换失败"));
          if (res.ok) await fetchProducts();
        };

        // 绑定取消按钮
        modal.querySelector('#cancelAddr').onclick = function() {
          document.body.removeChild(modal);
        };

        // 点击背景关闭
        modal.onclick = function(e) {
          if (e.target === modal) {
            document.body.removeChild(modal);
          }
        };

        return; // 等待用户选择
      }
    }

    // 如果没有地址或获取失败，使用手动输入
    addr = prompt("请输入收货地址（格式：姓名 / 电话 / 详细地址）\n\n注意：地址必须与您在个人中心保存的地址完全匹配");
    if (!addr) return;

    const res = await apiFetch("/user/api/orders", { method: "POST", body: JSON.stringify({ productId: prodId, address: addr })});
    alert(res.data?.message || (res.ok ? "下单成功" : "兑换失败"));
    if (res.ok) await fetchProducts();

  } catch (error) {
    console.error('兑换失败:', error);

    // 出错时使用手动输入
    const addr = prompt("请输入收货地址（格式：姓名 / 电话 / 详细地址）\n\n注意：地址必须与您在个人中心保存的地址完全匹配");
    if (!addr) return;

    const res = await apiFetch("/user/api/orders", { method: "POST", body: JSON.stringify({ productId: prodId, address: addr })});
    alert(res.data?.message || (res.ok ? "下单成功" : "兑换失败"));
    if (res.ok) await fetchProducts();
  }
}

/* 商户控制台 (上架/订单/提现) */
async function initMerchantDashboard() {
  await fetchMerchantProducts();
  await fetchMerchantOrders();
  await fetchMerchantWithdrawals();
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

// 待审核列表查询：适配后端字段和返回格式
// 待审核列表查询：适配你的apiFetch返回格式（ok/data）
// 修复语法错误 + 优化按钮样式，确保驳回按钮显示
async function fetchPendingTrips() {
  // 接口路径按你后端实际路径调整，比如/admin/trips/pending
  const res = await apiFetch("/admin/trips_pending");
  const el = document.getElementById("pendingTrips");
  if (!el) return;
  el.innerHTML = "";

  // 核心调整：用res.ok判断，res.data.trips取列表（你的apiFetch返回data是后端的完整响应）
  const items = (res.ok && Array.isArray(res.data.data?.trips)) ? res.data.data.trips : [];
  // 统计待审核数量（保留原有逻辑）
  setText("metricPendingTrips", items.length);

  if (items.length === 0) {
    el.innerHTML = "<div class='empty-state'>暂无待审。</div>";
    return;
  }

  // 渲染列表：字段适配（username/period），优化按钮样式确保显示
  items.forEach(t => {
    const node = document.createElement("div");
    node.className = "card";
    // 优化布局：避免按钮被挤压，调整样式确保驳回按钮可见
    node.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px">
      <div style="flex:1">
        <p style="margin:0"><strong>${t.username || '未知用户'}</strong></p>
        <p style="color:#6b7280;margin-top:6px">周期：${t.period || '未知'}</p>
        <p style="color:#6b7280;margin-top:4px">${t.mode} · ${t.distance || 0} km</p>
        ${t.note ? `<p style="color:#6b7280;margin-top:4px;font-size:12px">备注：${t.note}</p>` : ""}
      </div>
      <div style="display:flex;gap:8px;align-items:center">
        <!-- 通过按钮：保留原有样式 -->
        <button class="btn" onclick="adminDecideTrip(${t.id}, true)">通过</button>
        <!-- 驳回按钮：修改样式类为btn-danger，确保视觉可见，去掉white-space:nowrap避免挤压 -->
        <button class="btn" onclick="adminDecideTrip(${t.id}, false)">驳回</button>
      </div>
    </div>`;
    el.appendChild(node);
  });
}

// 审核操作：适配你的apiFetch返回格式
async function adminDecideTrip(id, approve) {
  // 驳回时弹窗输入原因（保留原有逻辑）
  let rejectReason = "";
  if (!approve) {
    rejectReason = prompt("请输入驳回原因（必填）：");

    // ========== 核心修改：先判断是否点击取消（返回null） ==========
    if (rejectReason === null) {
      // 用户点击取消，直接返回，不提示任何信息
      return;
    }

    // 再判断是否输入空内容（用户点确定但没填）
    rejectReason = rejectReason.trim();
    if (rejectReason === "") {
      alert("驳回原因不能为空！");
      return;
    }
  }

  if (!confirm(approve ? "确认通过并发放积分？" : `确认驳回【原因：${rejectReason}】？`)) return;

  try {
    const res = await apiFetch(`/admin/trips_pending/${id}/decide`, {
      method: "POST",
      body: JSON.stringify({ approve: approve, rejectReason: rejectReason })
    });

    const message = res.data.message || (res.ok ? "操作成功" : "操作失败");
    alert(message);

    if (res.ok) await fetchPendingTrips();
  } catch (err) {
    console.error("审核操作失败：", err);
    alert("审核操作失败，请稍后重试！");
  }
}

// 修复setText函数的语法错误（关键！）
function setText(elementId, text) {
  const el = document.getElementById(elementId);
  if (el) el.textContent = text; // 补充分号，闭合逻辑
}

async function fetchWithdrawalRequests() {
  console.log("fetchWithdrawalRequests: 开始获取提现申请...");
  const res = await apiFetch("/admin/api/withdrawals/pending");
  console.log("fetchWithdrawalRequests: API响应", res);
  const el = document.getElementById("withdrawalRequests");
  if (!el) {
    console.error("fetchWithdrawalRequests: 未找到withdrawalRequests元素");
    return;
  }
  el.innerHTML = "";

  if (!res.ok) {
    console.error("fetchWithdrawalRequests: API请求失败", res.status, res.data);
    el.innerHTML = `<div class='empty-state' style='color: red;'>获取提现申请失败：${res.data.message || '未知错误'}</div>`;
    return;
  }

  // 尝试多种可能的返回格式
  let items = [];
  if (res.ok) {
    console.log("fetchWithdrawalRequests: 原始响应数据", res.data);
    if (Array.isArray(res.data.data?.items)) {
      items = res.data.data.items;
    } else if (Array.isArray(res.data.items)) {
      items = res.data.items;
    } else if (Array.isArray(res.data)) {
      items = res.data;
    }
  }
  console.log("fetchWithdrawalRequests: 提现申请列表", items);
  setText("metricWithdrawals", items.length);
  if (items.length === 0) { el.innerHTML = "<div class='empty-state'>暂无提现申请</div>"; return; }
  items.forEach(w => {
    const node = document.createElement("div");
    node.className = "card";
    node.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center"><div style="flex:1"><p style="margin:0"><strong>${w.merchantId || w.merchantName}</strong></p><p style="color:#6b7280;margin-top:6px">积分：${w.points} (${w.amount ? w.amount.toFixed(2) : (w.points/100).toFixed(2)}元)</p><p style="color:#6b7280;margin-top:4px;font-size:12px">${w.withdrawal_no || ''}</p></div><div style="display:flex;gap:12px"><button class="btn" onclick="adminDecideWithdrawal('${w.id}', true)" style="padding:10px 24px;font-size:14px;font-weight:500;min-width:80px;">批准</button><button class="btn" onclick="adminDecideWithdrawal('${w.id}', false)" style="padding:10px 24px;font-size:14px;font-weight:500;min-width:80px;background-color:#dc3545;border-color:#dc3545;">拒绝</button></div></div>`;
    el.appendChild(node);
  });
}
async function adminDecideWithdrawal(id, approve) {
  if (!confirm(approve ? "批准提现？" : "拒绝提现？")) return;
  const res = await apiFetch(`/admin/api/admin/withdrawals/${id}/decide`, { method: "POST", body: JSON.stringify({ approve })});
  alert(res.data?.message || (res.ok ? "操作成功" : "操作失败"));
  if (res.ok) fetchWithdrawalRequests();
}
async function fetchPointRecords() {
  console.log("fetchPointRecords: 开始获取积分记录...");
  const res = await apiFetch("/admin/api/points/records");
  console.log("fetchPointRecords: API响应", res);
  console.log("fetchPointRecords: res.data", res.data);
  console.log("fetchPointRecords: res.data.items", res.data?.items);
  const el = document.getElementById("pointRecords");
  if (!el) return;
  el.innerHTML = "";

  if (!res.ok) {
    console.error("fetchPointRecords: API请求失败", res);
    el.innerHTML = `<div class='empty-state' style='color: red;'>获取积分记录失败：${res.data?.message || '未知错误'}</div>`;
    return;
  }

  // 尝试多种可能的返回格式
  let items = [];
  if (Array.isArray(res.data.items)) {
    items = res.data.items;
    console.log("fetchPointRecords: 使用res.data.items，长度", items.length);
  } else if (Array.isArray(res.data)) {
    items = res.data;
    console.log("fetchPointRecords: 使用res.data，长度", items.length);
  } else if (res.data && res.data.data && Array.isArray(res.data.data.items)) {
    items = res.data.data.items;
    console.log("fetchPointRecords: 使用res.data.data.items，长度", items.length);
  }

  console.log("fetchPointRecords: 积分记录列表", items);

  const totalPoints = items.reduce((sum, r) => sum + (Number(r.points) || 0), 0);
  setText("metricPoints", items.length ? `${totalPoints > 0 ? "+" : ""}${totalPoints}` : "0");

  if (items.length === 0) {
    el.innerHTML = "<div class='empty-state'>暂无记录</div>";
    return;
  }

  items.forEach(r => {
    const node = document.createElement("div");
    node.className = "list-row";
    const pointColor = r.points > 0 ? 'green' : 'red';
    const pointSign = r.points > 0 ? '+' : '';

    // 判断是用户还是商户
    let userType = '未知';
    if (r.username) {
      if (r.username.startsWith('U')) {
        userType = '用户';
      } else if (r.username.startsWith('M')) {
        userType = '商户';
      } else if (r.username.startsWith('A')) {
        userType = '管理员';
      }
    }

    node.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid #eee; background-color: ${r.points > 0 ? 'rgba(46, 204, 113, 0.05)' : 'rgba(231, 76, 60, 0.05)'};">
        <div style="flex:1;">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            <span style="color:#666; font-size:12px;">${new Date(r.time).toLocaleString()}</span>
            <span style="padding:2px 8px; background: ${userType === '用户' ? '#3498db' : userType === '商户' ? '#f39c12' : userType === '管理员' ? '#e74c3c' : '#999'}; color:white; border-radius:12px; font-size:11px;">
              ${userType}
            </span>
          </div>
          <div style="color:#333; font-weight:500; margin-bottom:4px;">${r.reason || r.type}</div>
          <div style="color:#666; font-size:14px;">
            ${r.username ? `<span style="margin-right:15px;">账号: ${r.username}</span>` : ''}
            ${r.balance !== undefined ? `余额: ${r.balance} 积分` : ''}
          </div>
          ${r.goods_name ? `<div style="color:#999; font-size:12px; margin-top:4px;">商品: ${r.goods_name}</div>` : ''}
          ${r.exchange_status ? `<div style="color:#999; font-size:12px; margin-top:2px;">状态: ${r.exchange_status}</div>` : ''}
        </div>
        <div style="text-align:right;">
          <div style="font-size:20px; font-weight:bold; color: ${pointColor};">
            ${pointSign}${r.points}
          </div>
          <div style="font-size:12px; color:#666; margin-top:4px;">积分</div>
        </div>
      </div>
    `;
    el.appendChild(node);
  });
}




/* ==========================================================
   积分兑换规则管理（point_rules.html 使用）
   ========================================================== */

// 本地缓存的规则列表（从后台获取）
var POINT_RULES = [];

/* ----- 1. 初始化页面 ----- */
function initPointRules() {
  fetch("/api/point-rules")
    .then(res => res.json())
    .then(data => {
      POINT_RULES = data;
      renderPointRuleTable();
    })
    .catch(err => {
      console.error(err);
      alert("加载积分规则失败");
    });
}

/* ----- 2. 渲染表格 ----- */
function renderPointRuleTable() {
  const table = document.getElementById("ruleTable");
  table.innerHTML = "";

  POINT_RULES.forEach((r, i) => {
    table.innerHTML += `
      <tr>
        <td><input class="input" value="${r.mode}" onchange="updateRule(${i}, 'mode', this.value)"></td>
        <td><input class="input" type="number" step="0.01" value="${r.rate}" onchange="updateRule(${i}, 'rate', parseFloat(this.value))"></td>
        <td>
          <button class="btn-mini red" onclick="deletePointRule(${i})">删除</button>
        </td>
      </tr>
    `;
  });
}

/* ----- 3. 修改内存中的规则对象 ----- */
function updateRule(index, field, value) {
  POINT_RULES[index][field] = value;
}

/* ----- 4. 删除规则 ----- */
function deletePointRule(index) {
  if (!confirm("确定删除此规则？")) return;
  POINT_RULES.splice(index, 1);
  renderPointRuleTable();
}

/* ----- 5. 新增规则 ----- */
function addPointRule() {
  POINT_RULES.push({
    mode: "新方式",
    rate: 1.0
  });
  renderPointRuleTable();
}

/* ----- 6. 保存所有规则（提交后台） ----- */
function savePointRules() {
  fetch("/api/point-rules/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(POINT_RULES)
  })
    .then(res => res.json())
    .then(res => {
      if (res.success) {
        alert("规则已成功保存！");
      } else {
        alert("保存失败：" + res.message);
      }
    })
    .catch(err => {
      console.error(err);
      alert("保存失败！");
    });
}


/*************************************************
 * 账户管理功能初始化
 *************************************************/
function initAdminUsers() {
  loadUserList();
  loadMerchantList();
}

/*************************************************
 * TAB 切换（用户 / 商户）
 *************************************************/
function switchUserTab(type) {
  const userPanel = document.getElementById("userPanel");
  const merchantPanel = document.getElementById("merchantPanel");

  // 修复选择器错误 - 使用正确的按钮选择器
  document.querySelectorAll(".tab-row .btn").forEach(b => b.classList.remove("active"));

  if (type === "user") {
    document.querySelectorAll(".tab-row .btn")[0].classList.add("active");
    userPanel.style.display = "block";
    merchantPanel.style.display = "none";
  } else {
    document.querySelectorAll(".tab-row .btn")[1].classList.add("active");
    userPanel.style.display = "none";
    merchantPanel.style.display = "block";
  }
}

/*************************************************
 * 数据加载：用户
 *************************************************/
async function loadUserList() {
  try {
    const res = await fetch("/admin/api/users");
    const data = await res.json();
    window._allUsers = data.users;
    renderUserTable(data.users);
  } catch (err) {
    console.error("用户数据加载失败", err);
  }
}

/*************************************************
 * 数据加载：商户
 *************************************************/
async function loadMerchantList() {
  try {
    const res = await fetch("/admin/api/merchants");
    const data = await res.json();
    window._allMerchants = data.merchants;
    renderMerchantTable(data.merchants);
  } catch (err) {
    console.error("商户数据加载失败", err);
  }
}

/*************************************************
 * 渲染用户表格
 *************************************************/
function renderUserTable(list) {
  const box = document.getElementById("userTable");
  box.innerHTML = "";

  // 强制设置表格为固定布局
  const table = box.closest('table');
  if (table) {
    table.style.tableLayout = 'fixed';
    table.style.width = '100%';  // 铺满整个容器
  }

  list.forEach(u => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${u.username}</td>
      <td>${u.email || "—"}</td>
      <td>
        <span class="pill ${u.status === "frozen" ? "orange" : ""}">
          ${u.status === "frozen" ? "已冻结" : "正常"}
        </span>
      </td>
      <td>
        <span>
          <button class="btn small" onclick="${
            u.status === "frozen" ? `unfreezeUser('${u.id}')` : `freezeUser('${u.id}')`
          }">${u.status === "frozen" ? '解冻' : '冻结'}</button>
          <button class="btn small danger" onclick="deleteUser('${u.id}')">删除</button>
        </span>
      </td>
    `;

    box.appendChild(row);
  });
}

/*************************************************
 * 渲染商户表格
 *************************************************/
function renderMerchantTable(list) {
  const box = document.getElementById("merchantTable");
  box.innerHTML = "";

  // 强制设置表格为固定布局
  const table = box.closest('table');
  if (table) {
    table.style.tableLayout = 'fixed';
    table.style.width = '100%';  // 铺满整个容器
  }

  list.forEach(m => {
    const row = document.createElement("tr");

    const statusPill =
      m.status === "pending" ? "pill orange" :
      m.status === "frozen" ? "pill danger" :
      "pill";

    const statusText =
      m.status === "pending" ? "待审核" :
      m.status === "frozen" ? "已冻结" :
      "正常";

    row.innerHTML = `
      <td>${m.username}</td>
      <td>${m.phone || "—"}</td>
      <td>
        <span class="${statusPill}">${statusText}</span>
      </td>
      <td>
          ${
            m.status === "pending"
              ? `<button class="btn small" onclick="approveMerchant('${m.id}')">通过</button>
                  <button class="btn small danger" onclick="rejectMerchant('${m.id}')">拒绝</button>`
              : ""
          }
          ${
            m.status === "frozen"
              ? `<button class="btn small" onclick="unfreezeMerchant('${m.id}')">解冻</button>`
              : `<button class="btn small danger" onclick="freezeMerchant('${m.id}')" >冻结</button>`
          }
          <button class="btn small danger" onclick="deleteMerchant('${m.id}')">删除</button>
      </td>
    `;

    box.appendChild(row);
  });
}

/*************************************************
 * 用户 API 操作
 *************************************************/
async function freezeUser(id) {
  await fetch(`/admin/api/users/${id}/freeze`, {method:"POST"});
  loadUserList();
}
async function unfreezeUser(id) {
  await fetch(`/admin/api/users/${id}/unfreeze`, {method:"POST"});
  loadUserList();
}
async function deleteUser(id) {
  if (!confirm("确定删除该用户？")) return;
  await fetch(`/admin/api/users/${id}`, {method:"DELETE"});
  loadUserList();
}

/*************************************************
 * 商户 API 操作
 *************************************************/
async function approveMerchant(id) {
  await fetch(`/admin/api/merchant/approve/${id}`, {method:"POST"});
  loadMerchantList();
}
async function rejectMerchant(id) {
  await fetch(`/admin/api/merchant/reject/${id}`, {method:"POST"});
  loadMerchantList();
}
async function freezeMerchant(id) {
  await fetch(`/admin/api/merchants/${id}/freeze`, {method:"POST"});
  loadMerchantList();
}
async function unfreezeMerchant(id) {
  await fetch(`/admin/api/merchants/${id}/unfreeze`, {method:"POST"});
  loadMerchantList();
}
async function deleteMerchant(id) {
  if (confirm("确定要删除这个商户吗？")) {
    await fetch(`/admin/api/merchants/${id}`, {method:"DELETE"});
    loadMerchantList();
  }
}

/*************************************************
 * 搜索
 *************************************************/
function filterAccountList() {
  const q = document.getElementById("searchInput").value.toLowerCase();

  // 修复选择器错误 - 使用正确的按钮选择器
  const activeTab = document.querySelector(".tab-row .btn.active");
  if (activeTab && activeTab.innerText === "用户列表") {
    renderUserTable(window._allUsers.filter(u =>
      (u.username + (u.email || "") + (u.phone || "")).toLowerCase().includes(q)
    ));
  } else {
    // 修复商户数据字段名 - 使用username而不是merchantName，phone而不是contact
    renderMerchantTable(window._allMerchants.filter(m =>
      (m.username + (m.email || "") + (m.phone || "")).toLowerCase().includes(q)
    ));
  }
}


/* ============================================================
   用户个人中心（user_profile.html）
   ============================================================ */

/* ----- 1. 页面初始化 ----- */
function initUserProfile() {
  fetchUserInfo();
}


/* ----- 2. 拉取用户信息（头像、昵称、积分等） ----- */
function fetchUserInfo() {
  // 1. 先处理用户基本信息，添加详细日志和错误处理
  fetch("/user/user_info")
    .then(res => {
      // 校验响应状态是否成功（200-299）
      if (!res.ok) {
        throw new Error(`请求失败，状态码：${res.status}`);
      }
      return res.json();
    })
    .then(data => {
      // 打印返回数据，方便调试（按 F12 看控制台）
      console.log("后端返回的用户信息：", data);

      // 处理后端返回的错误信息
      if (data.error) {
        alert(`加载失败：${data.error}`);
        // 未登录则跳回登录页
        if (data.error === "未登录") {
          window.location.href = "{{ url_for('user.login') }}";
        }
        return;
      }

      // 填入个人资料输入框（现在字段名完全匹配）
      document.getElementById("profileNickname").value = data.nickname || "";
      document.getElementById("profileAccount").value  = data.username || "";
      document.getElementById("profilePassword").value = data.password || "";
      document.getElementById("profilePhone").value    = data.phone || "";
      document.getElementById("profileEmail").value    = data.email || "";

    })
    .catch(err => {
      console.error("用户信息加载失败详情：", err);
      alert(`加载用户信息失败：${err.message}`);
    });

  // 2. 积分数据（添加错误处理）
  fetch("/user/user_profile/user_points")
    .then(res => {
      if (!res.ok) throw new Error(`积分请求失败：${res.status}`);
      return res.json();
    })
    .then(data => {
      document.getElementById("userPoints").innerText = data.points || 0;
      document.getElementById("userTotalEarn").innerText = data.earned || 0;
      document.getElementById("userTotalUsed").innerText = data.used || 0;
    })
    .catch(err => {
      console.error("积分数据加载失败：", err);
      document.getElementById("userPoints").innerText = "加载失败";
      document.getElementById("userTotalEarn").innerText = "加载失败";
      document.getElementById("userTotalUsed").innerText = "加载失败";
    });

  // 3. 积分流水（添加错误处理+兼容空数据）
// 兑换记录（最终版：容错HTML返回）
fetch("/user/user_profile/user_orders")
  .then(res => {
    console.log("兑换记录请求状态：", res.status);
    if (!res.ok) {
      throw new Error(`兑换记录请求失败：状态码${res.status}`);
    }
    // 先获取文本，判断是否是HTML，再解析JSON
    return res.text().then(text => {
      // 如果返回的是HTML（含<），直接返回空数组
      if (text.includes('<')) {
        console.warn("兑换记录接口返回HTML，按空数据处理");
        return [];
      }
      // 是JSON则解析
      try {
        return JSON.parse(text);
      } catch (e) {
        console.error("兑换记录JSON解析失败：", e);
        return [];
      }
    });
  })
  .then(list => {
    console.log("兑换记录数据：", list);
    renderList("orderHistory", list, "暂无兑换记录");
  })
  .catch(err => {
    console.error("兑换记录catch块错误：", err);
    // 仅非404错误弹窗（避免路径错干扰）
    if (!err.message.includes("404")) {
      alert("兑换记录查询失败，请稍后重试！");
    }
    renderList("orderHistory", [], "暂无兑换记录");
  });

// 积分流水也加同样的HTML容错（复制上面的逻辑，改路径和domId即可）
fetch("/user/user_profile/user_history")
  .then(res => {
    console.log("积分流水请求状态：", res.status);
    if (!res.ok) {
      throw new Error(`积分流水请求失败：状态码${res.status}`);
    }
    return res.text().then(text => {
      if (text.includes('<')) {
        console.warn("积分流水接口返回HTML，按空数据处理");
        return [];
      }
      try {
        return JSON.parse(text);
      } catch (e) {
        console.error("积分流水JSON解析失败：", e);
        return [];
      }
    });
  })
  .then(list => {
    console.log("积分流水数据：", list);
    renderList("pointHistory", list, "暂无流水数据");
  })
  .catch(err => {
    console.error("积分流水catch块错误：", err);
    if (!err.message.includes("404")) {
      alert("积分流水查询失败，请稍后重试！");
    }
    renderList("pointHistory", [], "暂无流水数据");
  });
}

// 补全缺失的 renderList 函数（否则流水/订单会报错）
function renderList(domId, list, emptyText = "暂无数据") {
  const box = document.getElementById(domId);
  // 防御：DOM元素不存在时不报错
  if (!box) {
    console.warn(`未找到ID为${domId}的DOM元素`);
    return;
  }
  box.innerHTML = "";

  // 空数据处理：支持自定义文案（区分流水/兑换）
  if (!Array.isArray(list) || list.length === 0) {
    box.innerHTML = `<div style="padding: 20px; text-align: center; color: #999;">${emptyText}</div>`;
    return;
  }

  // 渲染列表（根据DOM ID自动适配流水/兑换的字段）
  list.forEach(item => {
    const row = document.createElement("div");
    row.className = "list-row";
    row.style = "padding: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;";

    // 区分积分流水和兑换记录的字段渲染
    let title, time, value;
    if (domId === "pointHistory") {
      // 积分流水：适配后端返回的字段
      title = item.reason || "未知变动"; // 变动原因（出行/兑换商品等）
      time = item.create_time || "";    // 变动时间
      value = `${item.points > 0 ? '+' : ''}${item.points || 0}`; // 变动积分（+号区分获得/扣除）
      // 积分正负加颜色（可选，体验更好）
      value = `<span style="color: ${item.points > 0 ? 'green' : 'red'}">${value}</span>`;
    } else if (domId === "orderHistory") {
      // 兑换记录：适配后端返回的字段
      title = item.goods_name || "未知商品"; // 兑换商品名称
      time = item.exchange_time || "";       // 兑换时间
      value = `- ${item.use_points || 0}`;   // 消耗积分（固定减号）
      value = `<span style="color: red">${value}</span>`;
    } else {
      // 通用兜底（兼容其他列表）
      title = item.title || item.description || "未知记录";
      time = item.time || item.create_time || "";
      value = item.value || item.points || 0;
    }

    row.innerHTML = `
      <div>${title}</div>
      <div>${time}</div>
      <div>${value}</div>
    `;
    box.appendChild(row);
  });
}

/* ----- 3. 更新个人资料 ----- */
// 全局变量：防止重复提交的锁
var isSubmitting = false;

function saveUserProfile() {
  // 1. 校验是否处于编辑模式（避免未编辑就提交）
  const editBtn = document.getElementById("editBtn");
  if (editBtn.innerText !== "取消") {
    alert("请先点击「编辑」按钮进入编辑模式！");
    return;
  }

  // 2. 防重复提交：如果正在提交，直接返回
  if (isSubmitting) {
    alert("正在保存中，请稍候...");
    return;
  }

  // 3. 获取DOM元素并判空（避免元素不存在导致报错）
  const nicknameEl = document.getElementById("profileNickname");
  const accountEl = document.getElementById("profileAccount");
  const passwordEl = document.getElementById("profilePassword");
  const phoneEl = document.getElementById("profilePhone");
  const emailEl = document.getElementById("profileEmail");

  if (!nicknameEl || !accountEl || !passwordEl || !phoneEl || !emailEl) {
    alert("页面元素加载异常，请刷新重试！");
    return;
  }

  // 4. 获取输入值并做前端校验
  const nickname = nicknameEl.value.trim();
  const phone = phoneEl.value.trim();
  const email = emailEl.value.trim();
  const password = passwordEl.value.trim(); // 密码（注意：仅当不是******时才提交）

  // 基础校验
  if (!nickname) {
    alert("昵称不能为空！");
    nicknameEl.focus(); // 聚焦到错误输入框
    return;
  }

  // 手机号格式校验（11位数字）
  if (phone && !/^1[3-9]\d{9}$/.test(phone)) {
    alert("请输入正确的11位手机号！");
    phoneEl.focus();
    return;
  }

  // 邮箱格式校验
  if (email && !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
    alert("请输入正确的邮箱格式！");
    emailEl.focus();
    return;
  }

  // 5. 构造提交数据（仅提交需要修改的字段，排除账号/默认密码）
  const body = {
    nickname: nickname,
    phone: phone,
    email: email
  };
  // 仅当密码不是默认的******时，才提交密码（避免覆盖原有密码）
  if (password !== "******" && password) {
    body.password = password;
  }
  // 账号不允许修改，移除account字段
  // body.account = accountEl.value; // 注释掉，禁止修改账号

  // 6. 设置加载状态，防止重复提交
  isSubmitting = true;
  const saveBtn = document.getElementById("saveBtn");
  const originalBtnText = saveBtn.innerText;
  saveBtn.innerText = "保存中...";
  saveBtn.disabled = true;

  // 7. 发送请求（完善错误处理+响应解析）
  fetch("/user/user_profile/user_update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  })
  .then(res => {
    // 先校验响应状态码（200-299为成功）
    if (!res.ok) {
      throw new Error(`请求失败：${res.status}`);
    }
    return res.json();
  })
  .then(data => {
    // 处理后端返回的业务提示
    if (data.error) {
      alert(`修改失败：${data.error}`);
    } else {
      alert(data.message || "资料已更新！");
      toggleEdit(); // 退出编辑模式
      // 可选：重新拉取最新的用户信息，保证页面数据同步
      fetchUserInfo();
    }
  })
  .catch(err => {
    // 处理网络错误/解析错误等
    console.error("资料更新失败：", err);
    alert("修改失败！请检查网络或稍后重试。");
  })
  .finally(() => {
    // 8. 恢复按钮状态，释放提交锁
    isSubmitting = false;
    saveBtn.innerText = originalBtnText;
    saveBtn.disabled = false;
  });
}
/* ----- 5. 修改密码（可选） ----- */
function changePassword() {
  const oldPwd = document.getElementById("oldPassword").value;
  const newPwd = document.getElementById("newPassword").value;

  if (!oldPwd || !newPwd) {
    alert("请输入完整信息");
    return;
  }

  fetch("/api/user/change-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ old_password: oldPwd, new_password: newPwd })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert("密码修改成功");
        document.getElementById("oldPassword").value = "";
        document.getElementById("newPassword").value = "";
      } else {
        alert("修改失败：" + data.message);
      }
    })
    .catch(err => {
      console.error("修改密码失败", err);
      alert("修改密码时发生错误");
    });
}

// 查看订单详情
function viewOrderDetails(orderId) {
  // 假设有一个接口可以获取订单的详细信息
  fetch(`/api/get-order-details/${orderId}`)
    .then(response => response.json())
    .then(data => {
      const orderDetailsContainer = document.getElementById('orderDetails');
      orderDetailsContainer.innerHTML = `
        <p><strong>用户ID：</strong>${data.order.userId}</p>
        <p><strong>商品：</strong>${data.order.productName}</p>
        <p><strong>订单地址：</strong>${data.order.address}</p>
        <p><strong>订单状态：</strong>${data.order.status}</p>
        <button class="btn" onclick="processOrder(${data.order.id})">处理订单</button>
      `;
    })
    .catch(error => console.error('Error fetching order details:', error));
}

// 处理订单
function processOrder(orderId) {
  // 假设有一个接口可以处理订单（比如标记订单为已处理）
  fetch(`/api/process-order/${orderId}`, {
    method: 'POST',
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('订单已处理');
      fetchOrders(); // 刷新订单列表
    } else {
      alert('订单处理失败');
    }
  })
  .catch(error => console.error('Error processing order:', error));
}

// 获取商家的积分余额和兑换信息
function fetchMerchantPoints() {
  // 获取商户的积分和兑换信息
  console.log('正在获取商户积分信息...');
  fetch('/merchant/api/get-merchant-points')
    .then(response => {
      console.log('响应状态:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (data.error) {
        console.error('获取积分失败:', data.error);
        const pointsInfoContainer = document.getElementById('merchantPointsInfo');
        if (pointsInfoContainer) {
          pointsInfoContainer.innerHTML = `<p style="color: red;">${data.error}</p>`;
        }
        return;
      }

      const pointsInfoContainer = document.getElementById('merchantPointsInfo');
      if (!pointsInfoContainer) return;

      const points = data.points || 0; // 商家的积分余额
      const exchangeRate = data.exchangeRate || 100; // 汇率（积分兑换人民币的比例）
      const currencySymbol = data.currencySymbol || '¥'; // 货币符号

      const convertedAmount = (points / exchangeRate).toFixed(2); // 转换成人民币金额
      pointsInfoContainer.innerHTML = `
        <p><strong>当前积分余额：</strong>${points.toLocaleString()} 积分</p>
        <p><strong>兑换汇率：</strong>1${currencySymbol} = ${exchangeRate}积分</p>
        <p><strong>可兑换金额：</strong>${currencySymbol}${convertedAmount}</p>
      `;
    })
    .catch(error => {
      console.error('Error fetching merchant points:', error);
      const pointsInfoContainer = document.getElementById('merchantPointsInfo');
      if (pointsInfoContainer) {
        pointsInfoContainer.innerHTML = '<p style="color: red;">加载积分信息失败</p>';
      }
    });
}

// 提交积分提现申请
function processWithdrawal() {
  const withdrawAmount = document.getElementById('withdrawAmount').value;
  if (!withdrawAmount || withdrawAmount <= 0) {
    alert('请输入有效的提现积分');
    return;
  }

  // 获取商家的积分余额和兑换汇率
  fetch('/merchant/api/get-merchant-points')
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (data.error) {
        alert('获取积分信息失败：' + data.error);
        return;
      }

      const points = data.points || 0; // 商家的积分余额
      const exchangeRate = data.exchangeRate || 100; // 汇率

      // 检查提现的积分是否小于等于商家余额
      if (withdrawAmount > points) {
        alert('您的积分余额不足');
        return;
      }

      const withdrawalAmount = (withdrawAmount / exchangeRate).toFixed(2); // 计算人民币金额

      if (!confirm(`确定要申请提现 ${withdrawAmount} 积分（约 ${withdrawalAmount} 元）吗？`)) {
        return;
      }

      // 调用后端接口申请提现
      fetch('/merchant/api/process-withdrawal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ withdrawAmount: withdrawAmount })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          alert(data.message || '提现申请成功');
          fetchMerchantPoints(); // 刷新积分信息
          // 清空输入框
          document.getElementById('withdrawAmount').value = '';
        } else {
          alert(data.message || '提现申请失败');
        }
      })
      .catch(error => {
        console.error('Error processing withdrawal:', error);
        alert('提现申请失败，请稍后重试');
      });
    })
    .catch(error => {
      console.error('Error fetching merchant points:', error);
      alert('获取积分信息失败，请稍后重试');
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
window.toResetPage = toResetPage;

// 管理员相关函数
window.fetchPendingTrips = fetchPendingTrips;
window.fetchWithdrawalRequests = fetchWithdrawalRequests;
window.adminDecideWithdrawal = adminDecideWithdrawal;

 
