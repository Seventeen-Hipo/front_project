// 页面加载完成后检查URL参数中的错误信息
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    if (error) {
        showError(error);
    }

    // 为所有输入框绑定输入事件（隐藏错误提示）
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', hideErrorOnInput);
    });
});

/**
 * 显示错误信息（不自动消失，直到用户操作）
 * @param {string} message - 错误提示内容
 */
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');

    if (!errorDiv || !errorText) return;

    errorText.textContent = message;
    errorDiv.style.display = 'block';

    // 触发过渡动画
    setTimeout(() => {
        errorDiv.style.opacity = '1';
        errorDiv.classList.add('show');
    }, 10);
}

/**
 * 隐藏错误信息
 */
function hideError() {
    const errorDiv = document.getElementById('errorMessage');
    if (!errorDiv) return;

    errorDiv.style.opacity = '0';
    setTimeout(() => {
        errorDiv.style.display = 'none';
        errorDiv.classList.remove('show');
    }, 300);
}

/**
 * 输入时隐藏错误提示
 */
function hideErrorOnInput() {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv && errorDiv.style.display === 'block') {
        hideError();
    }
}

/**
 * 处理登录表单提交（AJAX异步提交）
 * @param {Event} event - 表单提交事件
 */
async function handleLogin(event) {
    event.preventDefault(); // 阻止表单默认提交行为

    const form = document.getElementById('loginForm');
    const loginBtn = document.querySelector('.login-btn');
    const originalText = loginBtn.textContent;

    // 处理按钮加载状态
    loginBtn.disabled = true;
    loginBtn.textContent = '登录中...';
    loginBtn.style.opacity = '0.7';

    try {
        // 构建表单数据
        const formData = new FormData(form);

        // 发送登录请求
        const response = await fetch('/api/login', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // 登录成功状态处理
            loginBtn.textContent = '登录成功！';
            loginBtn.style.background = 'linear-gradient(135deg, #51cf66 0%, #69db7c 100%)';

            // 延迟跳转，展示成功反馈
            setTimeout(() => {
                // 优先读取URL中的next参数，无则跳首页
                const urlParams = new URLSearchParams(window.location.search);
                const nextPage = urlParams.get('next') || '/home';
                window.location.href = nextPage;
            }, 800);
        } else {
            // 登录失败，显示错误信息
            showError(data.message || '登录失败，请检查用户名和密码');

            // 恢复按钮状态
            loginBtn.disabled = false;
            loginBtn.textContent = originalText;
            loginBtn.style.opacity = '1';
        }
    } catch (error) {
        // 网络错误处理
        console.error('登录请求异常:', error);
        showError('网络错误，请稍后重试');

        // 恢复按钮状态
        loginBtn.disabled = false;
        loginBtn.textContent = originalText;
        loginBtn.style.opacity = '1';
    }
}