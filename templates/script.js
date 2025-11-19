// 自动生成账号
function generateAccount(role) {
    // 防止 admin 被生成
    if (role === "admin") role = "user";

    const prefix = {
        user: "U",
        merchant: "M"
    }[role] || "U";

    return prefix + Date.now();
}

// 注册
async function register() {
    let role = document.getElementById("role").value;

    // 阻止注册 admin
    if (role === "admin") {
        alert("前端不允许注册系统管理员账号！");
        return;
    }

    const email = document.getElementById("email").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const pwd = document.getElementById("password").value.trim();

    if (!email || !phone || !pwd) return alert("请填写完整信息！");

    const id = generateAccount(role);
    document.getElementById("generatedId").innerText = id;

    const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role, id, email, phone, password: pwd })
    });

    const data = await res.json();
    alert(data.message);
}

// 登录
async function login() {
    const id = document.getElementById("login_id").value.trim();
    const pwd = document.getElementById("login_password").value.trim();

    if (!id || !pwd) return alert("请填写账号和密码！");

    const res = await fetch("/api/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ id, password: pwd })
    });

    const data = await res.json();

    if (!data.success) return alert(data.message);

    // 保存账号功能（记住我）
    if (document.getElementById("rememberMe").checked) {
        localStorage.setItem("remember_id", id);
    } else {
        localStorage.removeItem("remember_id");
    }

    if (data.role === "user") location.href = "user_home.html";
    else if (data.role === "merchant") location.href = "merchant_home.html";
    else if (data.role === "admin") location.href = "admin_home.html";
}

// 忘记密码发送验证码
let countdown = 60;
async function sendCode() {
    const id = document.getElementById("fp_id").value.trim();
    const email = document.getElementById("fp_email").value.trim();

    if (!id || !email) return alert("请填写账号与邮箱！");

    const btn = document.getElementById("sendCodeBtn");
    btn.disabled = true;
    btn.innerText = `${countdown} 秒`;

    let timer = setInterval(() => {
        countdown--;
        btn.innerText = `${countdown} 秒`;
        if (countdown <= 0) {
            clearInterval(timer);
            btn.disabled = false;
            btn.innerText = "发送验证码";
            countdown = 60;
        }
    }, 1000);

    await fetch("/api/send-reset-code", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ id, email })
    });

    alert("验证码已发送，5 分钟内有效！");
}

// 重设密码
async function resetPassword() {
    const id = document.getElementById("rp_id").value.trim();
    const code = document.getElementById("rp_code").value.trim();
    const pwd = document.getElementById("rp_newpwd").value.trim();

    if (!id || !code || !pwd) return alert("请填写完整信息！");

    const res = await fetch("/api/reset-password", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ id, code, password: pwd })
    });

    const data = await res.json();
    alert(data.message);
}

// 自动填充记住的账号
window.addEventListener("DOMContentLoaded", () => {
    const savedId = localStorage.getItem("remember_id");
    if (savedId) {
        document.getElementById("login_id").value = savedId;
        document.getElementById("rememberMe").checked = true;
    }
});