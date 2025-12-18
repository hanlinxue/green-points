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
      background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%);
      color: #2c3e50;
      padding: 12px 20px;
      font-size: 15px;
      font-weight: 500;
      box-shadow: 0 2px 8px rgba(46,204,113,0.3);
      z-index: 9999;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #27AE60;
    }

    #welcomeBar .welcome-info {
      display: flex;
      align-items: center;
      gap: 15px;
    }

    #welcomeBar .role-badge {
      background: rgba(255,255,255,0.9);
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 700;
      color: #27AE60;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    #welcomeBar .role-user {
      background: rgba(255,255,255,0.9);
      color: #0099ff;
    }
    #welcomeBar .role-merchant {
      background: rgba(255,255,255,0.9);
      color: #ff9900;
    }
    #welcomeBar .role-admin {
      background: rgba(255,255,255,0.9);
      color: #ff4444;
    }

    #welcomeBar strong {
      color: #1a5c3a;
      font-size: 16px;
    }

    #welcomeBar .logout-btn {
      background: rgba(255,255,255,0.9);
      border: 2px solid #00b359;
      color: #27AE60;
      padding: 6px 18px;
      border-radius: 25px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      transition: all 0.3s;
      text-decoration: none;
      display: inline-block;
    }

    #welcomeBar .logout-btn:hover {
      background: #27AE60;
      color: white;
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(46,204,113,0.3);
    }

    /* 调整页面内容，避免被顶部栏遮挡 */
    body.has-welcome-bar {
      margin-top: 55px;
    }

    /* 特别处理dashboard类的页面 */
    body.has-welcome-bar .dashboard {
      margin-top: 0;
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