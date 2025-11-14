document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registerForm');
  const errorBox = document.getElementById('errorMessage');
  const errorText = document.getElementById('errorText');
  const btn = document.querySelector('.register-btn');
  const inputs = form.querySelectorAll('input');
  const params = new URLSearchParams(window.location.search);
  const preloadError = params.get('error');

  function showError(message) {
    if (!errorBox || !errorText) return;
    errorText.textContent = message;
    errorBox.style.display = 'block';
    requestAnimationFrame(() => {
      errorBox.classList.add('show');
    });
  }

  function hideError() {
    if (!errorBox) return;
    errorBox.classList.remove('show');
    setTimeout(() => { errorBox.style.display = 'none'; }, 200);
  }

  inputs.forEach(input => {
    input.addEventListener('input', hideError);
  });

  if (preloadError) {
    showError(preloadError);
  }

  window.handleRegister = async function(event) {
    event.preventDefault();
    const formData = new FormData(form);

    // 前端校验
    const username = formData.get('username').trim();
    const password = formData.get('password').trim();
    const usernameReg = /^[a-zA-Z0-9]{3,15}$/;

    if (!usernameReg.test(username)) {
      showError('用户名需为3-15位字母或数字');
      return;
    }
    if (password.length < 6 || password.length > 20) {
      showError('密码需为6-20位字符');
      return;
    }

    // 按钮状态
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = '注册中...';
    btn.style.opacity = '0.7';

    try {
      const resp = await fetch('/api/register', {
        method: 'POST',
        body: formData
      });
      const data = await resp.json();
      if (data.success) {
        btn.textContent = '注册成功！';
        btn.style.background = 'linear-gradient(135deg,#51cf66 0%,#69db7c 100%)';
        setTimeout(() => {
          window.location.href = '/login?success=注册成功，请登录';
        }, 900);
      } else {
        showError(data.message || '注册失败，请稍后重试');
        btn.disabled = false;
        btn.textContent = originalText;
        btn.style.opacity = '1';
      }
    } catch (error) {
      console.error('注册请求异常:', error);
      showError('网络错误，请稍后重试');
      btn.disabled = false;
      btn.textContent = originalText;
      btn.style.opacity = '1';
    }
  };
});