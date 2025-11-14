// 全局DOM元素引用
const fileInput = document.getElementById('fileInput');
const btnPredict = document.getElementById('btnPredict');
const resultBox = document.getElementById('result');
const previewImg = document.getElementById('preview');
const dropzone = document.getElementById('dropzone');
const progressBar = document.getElementById('progress');
const progressBarFill = document.getElementById('bar');
const predEl = document.getElementById('pred');
const confEl = document.getElementById('conf');
let currentFile = null;

// 1. 未登录检测：跳转到登录页
(async function checkLoginStatus() {
  try {
    const response = await fetch('/api/me', { credentials: 'include' });
    if (!response.ok) {
      redirectToLogin('请先登录后再访问动物识别功能');
      return;
    }
    const data = await response.json().catch(() => null);
    if (!(data && data.success)) {
      redirectToLogin('请先登录后再访问动物识别功能');
    }
  } catch (error) {
    redirectToLogin('请先登录后再访问动物识别功能');
  }
})();

// 登录跳转辅助函数
function redirectToLogin(errorMsg) {
  window.location.href = `/login?error=${encodeURIComponent(errorMsg)}&next=%2Fidentify`;
}

// 2. 图片处理：设置预览图
function setPreviewFile(file) {
  if (!file) return;
  const fileURL = URL.createObjectURL(file);
  previewImg.src = fileURL;
  previewImg.style.display = 'block';
  currentFile = file;
}

// 3. 按钮涟漪效果
btnPredict.addEventListener('click', function (e) {
  const x = e.offsetX;
  const y = e.offsetY;
  this.style.setProperty('--rX', `${x}px`);
  this.style.setProperty('--rY', `${y}px`);

  const ripple = document.createElement('span');
  ripple.style.position = 'absolute';
  ripple.style.left = `${x}px`;
  ripple.style.top = `${y}px`;
  ripple.style.width = '0';
  ripple.style.height = '0';
  ripple.style.borderRadius = '50%';
  ripple.style.background = 'rgba(255, 255, 255, .45)';
  ripple.style.transform = 'translate(-50%, -50%)';
  ripple.style.transition = 'width .45s ease, height .45s ease, opacity .45s ease';

  this.appendChild(ripple);

  requestAnimationFrame(() => {
    ripple.style.width = '300px';
    ripple.style.height = '300px';
    ripple.style.opacity = '0';
  });

  setTimeout(() => ripple.remove(), 480);
}, { passive: true });

// 4. 文件选择事件监听
fileInput.addEventListener('change', () => {
  setPreviewFile(fileInput.files[0]);
});

// 5. 拖拽上传功能
['dragenter', 'dragover'].forEach(eventType => {
  dropzone.addEventListener(eventType, (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropzone.classList.add('dragover');
  });
});

['dragleave', 'drop'].forEach(eventType => {
  dropzone.addEventListener(eventType, (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropzone.classList.remove('dragover');
  });
});

dropzone.addEventListener('drop', (e) => {
  const files = e.dataTransfer.files;
  if (files && files[0]) {
    setPreviewFile(files[0]);
  }
});

// 6. 识别按钮点击事件
btnPredict.addEventListener('click', async () => {
  const selectedFile = currentFile || fileInput.files[0];
  if (!selectedFile) {
    alert('请先选择图片');
    return;
  }

  // 构建FormData
  const formData = new FormData();
  formData.append('file', selectedFile);

  // 重置UI状态
  resultBox.classList.remove('show');
  resultBox.style.display = 'none';
  progressBar.style.display = 'block';
  progressBarFill.style.width = '0%';

  // 模拟进度条动画
  let progressWidth = 0;
  const progressTimer = setInterval(() => {
    progressWidth = Math.min(progressWidth + Math.random() * 12 + 5, 92);
    progressBarFill.style.width = `${progressWidth}%`;
  }, 220);

  try {
    // 发送识别请求
    const response = await fetch('/api/predict', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      if (response.status === 401) {
        redirectToLogin('登录状态已失效，请重新登录');
        return;
      }
      const errorData = await response.json().catch(() => ({ detail: '识别请求失败' }));
      throw new Error(errorData.detail || '识别请求失败');
    }

    const resultData = await response.json();

    // 完成进度条动画
    clearInterval(progressTimer);
    progressBarFill.style.width = '100%';
    setTimeout(() => {
      progressBar.style.display = 'none';
    }, 180);

    // 显示识别结果
    predEl.textContent = resultData.predicted_class;
    confEl.textContent = `准确率：${resultData.confidence}%`;
    resultBox.style.display = 'block';
    requestAnimationFrame(() => {
      resultBox.classList.add('show');
    });

    // 显示庆祝动画
    burst(resultBox);
  } catch (error) {
    // 错误处理
    clearInterval(progressTimer);
    progressBar.style.display = 'none';
    resultBox.style.display = 'block';
    resultBox.classList.add('show');
    predEl.textContent = '识别失败';
    confEl.textContent = error.message || '未知错误';
  }
});

// 7. 庆祝动画效果
function burst(anchorElement) {
  const dotCount = 14;
  const colors = ['#3bc9db', '#845ef7', '#34d399', '#f59e0b', '#ef4444'];

  for (let i = 0; i < dotCount; i++) {
    const dot = document.createElement('span');
    dot.style.position = 'absolute';
    dot.style.width = '8px';
    dot.style.height = '8px';
    dot.style.borderRadius = '50%';
    dot.style.background = colors[i % colors.length];
    dot.style.left = `${anchorElement.offsetLeft + anchorElement.offsetWidth / 2}px`;
    dot.style.top = `${anchorElement.offsetTop + 10}px`;
    dot.style.pointerEvents = 'none';
    dot.style.opacity = '0.95';

    document.body.appendChild(dot);

    // 计算动画轨迹
    const angle = (Math.PI * 2 / dotCount) * i;
    const distance = 40 + Math.random() * 40;
    const dx = Math.cos(angle) * distance;
    const dy = Math.sin(angle) * distance - 20;

    // 执行动画
    dot.animate([
      { transform: 'translate(0, 0) scale(1)', opacity: 1 },
      { transform: `translate(${dx}px, ${dy}px) scale(.6)`, opacity: 0 }
    ], {
      duration: 700,
      easing: 'cubic-bezier(.2, .7, .3, 1)',
      fill: 'forwards'
    }).onfinish = () => {
      dot.remove();
    };
  }
}