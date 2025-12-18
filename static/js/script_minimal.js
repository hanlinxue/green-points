// 最小化JavaScript文件 - 只包含必要的管理员功能

// API请求函数
async function apiFetch(url, options = {}) {
  const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
    ...(token && { 'X-CSRFToken': token })
  };
  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'same-origin'
  });
  return response;
}

// 文本设置函数
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

// 提现审核功能
async function adminDecideWithdrawal(id, approve) {
  if (!confirm(approve ? "批准提现？" : "拒绝提现？")) return;
  try {
    const res = await apiFetch(`/admin/api/admin/withdrawals/${id}/decide`, {
      method: "POST",
      body: JSON.stringify({ approve })
    });
    alert(res.data?.message || (res.ok ? "操作成功" : "操作失败"));
    if (res.ok) location.reload();
  } catch (error) {
    console.error('审核失败:', error);
    alert('操作失败，请重试');
  }
}

console.log('script_minimal.js 已加载');