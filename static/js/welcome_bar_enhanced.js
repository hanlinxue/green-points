// 添加顶部欢迎栏 - 增强版（可获取真实用户名）
(function() {
  'use strict';

  // 检查是否已经添加过欢迎栏
  if (document.getElementById('welcomeBar')) {
    return;
  }

  // 创建欢迎栏样式
  const style = document.createElement('style');
  style.textContent = `
    #welcomeBar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
      color: #ffffff;
      padding: 12px 30px;
      font-size: 14px;
      font-weight: 400;
      box-shadow: 0 4px 20px rgba(16, 185, 129, 0.25);
      z-index: 9999;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    #welcomeBar .welcome-info {
      display: flex;
      align-items: center;
      gap: 15px;
    }

    #welcomeBar .role-badge {
      background: rgba(255, 255, 255, 0.2);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 500;
      color: #ffffff;
      border: 1px solid rgba(255, 255, 255, 0.3);
      -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
      transition: all 0.3s ease;
    }

    #welcomeBar .role-badge:hover {
      background: rgba(255, 255, 255, 0.3);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    #welcomeBar .role-user {
      background: rgba(34, 197, 94, 0.3);
      border-color: rgba(34, 197, 94, 0.5);
    }
    #welcomeBar .role-user:hover {
      background: rgba(34, 197, 94, 0.4);
    }

    #welcomeBar .role-merchant {
      background: rgba(251, 191, 36, 0.3);
      border-color: rgba(251, 191, 36, 0.5);
    }
    #welcomeBar .role-merchant:hover {
      background: rgba(251, 191, 36, 0.4);
    }

    #welcomeBar .role-admin {
      background: rgba(239, 68, 68, 0.3);
      border-color: rgba(239, 68, 68, 0.5);
    }
    #welcomeBar .role-admin:hover {
      background: rgba(239, 68, 68, 0.4);
    }

    #welcomeBar strong {
      color: #ffffff;
      font-size: 16px;
      font-weight: 600;
      text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }

    #welcomeBar .logout-btn {
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.25);
      color: #ffffff;
      padding: 8px 20px;
      border-radius: 25px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      transition: all 0.3s ease;
      text-decoration: none;
      display: inline-block;
      -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
    }

    #welcomeBar .logout-btn:hover {
      background: rgba(239, 68, 68, 0.2);
      border-color: rgba(239, 68, 68, 0.4);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    }

    #welcomeBar span:not(.role-badge):not(strong) {
      color: rgba(255, 255, 255, 0.9);
      font-size: 14px;
    }

    /* 添加清新绿的光泽效果 */
    #welcomeBar::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.15),
        transparent
      );
      transition: left 0.5s;
    }

    #welcomeBar:hover::before {
      left: 100%;
    }

    /* 调整页面内容，避免被顶部栏遮挡 */
    body.has-welcome-bar {
      margin-top: 55px;
    }

    /* 特别处理dashboard类的页面 */
    body.has-welcome-bar .dashboard {
      margin-top: 0;
    }

    /* 添加绿叶装饰 */
    #welcomeBar::after {
      content: '🌿';
      position: absolute;
      right: 150px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 16px;
      opacity: 0.6;
      animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
      0%, 100% { transform: translateY(-50%) translateX(0); }
      50% { transform: translateY(-55%) translateX(3px); }
    }
  `;
  document.head.appendChild(style);

  // 获取当前页面的路径
  const currentPath = window.location.pathname;
  const isLoginPage = currentPath.includes('/login') || currentPath === '/' || currentPath === '/user';

  // 只在非登录页面显示欢迎栏
  if (!isLoginPage) {
    // 获取用户信息
    getUserInfo().then(userInfo => {
      if (userInfo) {
        createWelcomeBar(userInfo);
      }
    });
  }

  // 创建欢迎栏
  function createWelcomeBar(userInfo) {
    const welcomeBar = document.createElement('div');
    welcomeBar.id = 'welcomeBar';

    // 根据角色显示不同的信息类型
    let userDetail = userInfo.name;
    let infoType = '';

    if (userInfo.role === 'user') {
      infoType = '用户昵称：';
    } else if (userInfo.role === 'merchant') {
      infoType = '商户ID：';
    } else if (userInfo.role === 'admin') {
      infoType = '管理员ID：';
    }

    welcomeBar.innerHTML = `
      <div class="welcome-info">
        <span>你好，</span>
        <span class="role-badge role-${userInfo.role}">${userInfo.roleText}</span>
        <span>${infoType}</span>
        <strong>${userInfo.name}</strong>
      </div>
      <div>
        <a href="/user/user_out" class="logout-btn">退出登录</a>
      </div>
    `;

    // 添加到页面
    document.body.insertBefore(welcomeBar, document.body.firstChild);
    document.body.classList.add('has-welcome-bar');
  }

  // 获取用户信息的函数
  async function getUserInfo() {
    try {
      // 方法1: 通过API获取用户信息
      const response = await fetch('/user/api/current_user', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data && !data.error) {
          return {
            role: data.role,
            roleText: data.roleText,
            name: data.id || data.name
          };
        }
      }
    } catch (e) {
      console.log('API获取用户信息失败');
    }

    // 如果API成功获取到数据，直接返回
    // 如果失败，根据路径返回默认值
    let role = 'user';
    let roleText = '用户';
    let username = null;

    if (currentPath.includes('/admin/')) {
      role = 'admin';
      roleText = '系统管理员';
      username = '管理员';
    } else if (currentPath.includes('/merchant/')) {
      role = 'merchant';
      roleText = '商户';
      username = '商户';
    } else if (currentPath.includes('/user/')) {
      role = 'user';
      roleText = '用户';
      username = '用户';
    }

    // 返回用户信息
    return {
      role,
      roleText,
      name: username
    };
  }

})();