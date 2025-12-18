// 添加顶部欢迎栏
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
      background: linear-gradient(135deg, #1d2a41 0%, #2c3e50 100%);
      color: white;
      padding: 8px 20px;
      font-size: 14px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      z-index: 9999;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    #welcomeBar .welcome-info {
      display: flex;
      align-items: center;
      gap: 15px;
    }

    #welcomeBar .role-badge {
      background: rgba(255,255,255,0.2);
      padding: 4px 10px;
      border-radius: 15px;
      font-size: 12px;
      font-weight: 600;
    }

    #welcomeBar .role-user { background: rgba(52, 152, 219, 0.3); }
    #welcomeBar .role-merchant { background: rgba(46, 204, 113, 0.3); }
    #welcomeBar .role-admin { background: rgba(231, 76, 60, 0.3); }

    #welcomeBar .logout-btn {
      background: transparent;
      border: 1px solid rgba(255,255,255,0.5);
      color: white;
      padding: 5px 15px;
      border-radius: 5px;
      cursor: pointer;
      font-size: 13px;
      transition: all 0.3s;
      text-decoration: none;
      display: inline-block;
    }

    #welcomeBar .logout-btn:hover {
      background: rgba(255,255,255,0.2);
      border-color: white;
    }

    /* 调整页面内容，避免被顶部栏遮挡 */
    body.has-welcome-bar {
      margin-top: 44px;
    }

    /* 特别处理dashboard类的页面 */
    body.has-welcome-bar .dashboard {
      margin-top: 0;
    }
  `;
  document.head.appendChild(style);

  // 创建欢迎栏
  const welcomeBar = document.createElement('div');
  welcomeBar.id = 'welcomeBar';

  // 获取当前页面的路径和标题
  const currentPath = window.location.pathname;
  const isLoginPage = currentPath.includes('/login') || currentPath === '/' || currentPath === '/user';

  // 只在非登录页面显示欢迎栏
  if (!isLoginPage) {
    // 获取用户信息（需要从页面中提取或通过API获取）
    const userInfo = getUserInfo();

    if (userInfo) {
      welcomeBar.innerHTML = `
        <div class="welcome-info">
          <span>你好，</span>
          <span class="role-badge role-${userInfo.role}">${userInfo.roleText}</span>
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
  }

  // 获取用户信息的函数
  function getUserInfo() {
    // 尝试从页面中的导航栏获取信息
    const nav = document.querySelector('.dash-nav');
    if (nav) {
      // 检查是否是管理员页面
      if (window.location.pathname.includes('/admin/')) {
        const adminLinks = nav.querySelectorAll('a[href*="admin"]');
        if (adminLinks.length > 0) {
          // 管理员页面，从session或URL推断
          return {
            role: 'admin',
            roleText: '系统管理员',
            name: '管理员'
          };
        }
      }

      // 检查是否是商户页面
      if (window.location.pathname.includes('/merchant/')) {
        const merchantLinks = nav.querySelectorAll('a[href*="merchant"]');
        if (merchantLinks.length > 0) {
          // 商户页面
          return {
            role: 'merchant',
            roleText: '商户',
            name: '商户'
          };
        }
      }

      // 检查是否是用户页面
      if (window.location.pathname.includes('/user/')) {
        const userLinks = nav.querySelectorAll('a[href*="user"]');
        if (userLinks.length > 0) {
          // 用户页面
          return {
            role: 'user',
            roleText: '用户',
            name: '用户'
          };
        }
      }
    }

    // 如果无法确定，返回null
    return null;
  }

})();