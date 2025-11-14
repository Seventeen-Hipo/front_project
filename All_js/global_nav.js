async function updateNavActions() {
  try {
    const resp = await fetch('/api/me', { credentials: 'include' });
    if (!resp.ok) return;
    const data = await resp.json();
    if (data && data.success && data.user && data.user.username) {
      const nav = document.getElementById('navActions');
      if (nav) {
        const username = data.user.username;
        nav.innerHTML = `
          <div class="nav-user-box" style="display:flex;align-items:center;gap:10px;">
            <div class="avatar" style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#3bc9db,#845ef7);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;">
              ${username.substring(0,1) || 'U'}
            </div>
            <div class="user-info" style="display:flex;flex-direction:column;line-height:1.2;">
              <span style="font-weight:600;color:#1f2937;">欢迎，${username}</span>
              <span style="font-size:12px;color:#6b7280;">已登录</span>
            </div>
            <a class="nav-btn" href="/logout" style="margin-left:6px;">退出</a>
          </div>
        `;
      }
    }
  } catch (e) {
    console.warn('导航栏状态更新失败:', e);
  }
}

function highlightCurrentNav() {
  var path = location.pathname;
  if (path === '/') path = '/home';
  document.querySelectorAll('.nav-list a').forEach(function(a){
    if (a.getAttribute('href') === path) {
      a.classList.add('active');
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  updateNavActions();
  highlightCurrentNav();
});

