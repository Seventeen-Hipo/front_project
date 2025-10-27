// 获取DOM元素
const sliderWrapper = document.querySelector('.slider-wrapper');
const sliderItems = document.querySelectorAll('.slider-item');
const pagination = document.querySelector('.pagination');
const prevBtn = document.querySelector('.prev-btn');
const nextBtn = document.querySelector('.next-btn');

// 轮播图状态
let currentIndex = 0;
const slideCount = sliderItems.length;
let timer = null;

// 初始化分页器
function initPagination() {
  for (let i = 0; i < slideCount; i++) {
    const dot = document.createElement('div');
    dot.className = `dot ${i === 0 ? 'active' : ''}`;
    dot.dataset.index = i;
    pagination.appendChild(dot);
  }
}

// 切换轮播图
function switchSlide(index) {
  // 移动轮播容器
  sliderWrapper.style.transform = `translateX(-${index * 100}%)`;
  // 更新分页器激活状态
  document.querySelectorAll('.dot').forEach((dot, i) => {
    dot.className = `dot ${i === index ? 'active' : ''}`;
  });
  currentIndex = index;
}

// 自动轮播
function autoPlay() {
  timer = setInterval(() => {
    const nextIndex = (currentIndex + 1) % slideCount;
    switchSlide(nextIndex);
  }, 5000); // 5秒切换一次
}

// 处理滑动退出（监听触摸或鼠标滚轮事件）
function handleSlideExit() {
  let startY = 0;
  let endY = 0;

  // 触摸事件（移动端）
  sliderWrapper.addEventListener('touchstart', (e) => {
    startY = e.touches[0].clientY;
  });
  sliderWrapper.addEventListener('touchmove', (e) => {
    endY = e.touches[0].clientY;
  });
  sliderWrapper.addEventListener('touchend', () => {
    if (endY - startY < -100) { // 下滑距离超过100px则退出（这里模拟退出，实际可跳转到其他页面）
      alert('已退出轮播图');
      // 实际场景可执行：window.location.href = '其他页面路径';
    }
  });

  // 鼠标滚轮事件（PC端）
  sliderWrapper.addEventListener('wheel', (e) => {
    if (e.deltaY > 100) { // 鼠标滚轮向下滚动超过阈值则退出
      alert('已退出轮播图');
      // 实际场景可执行：window.location.href = '其他页面路径';
    }
  });
}

// 初始化事件监听
function initEventListeners() {
  // 分页器点击
  pagination.addEventListener('click', (e) => {
    if (e.target.classList.contains('dot')) {
      const index = parseInt(e.target.dataset.index);
      switchSlide(index);
      resetTimer();
    }
  });

  // 左右按钮点击
  prevBtn.addEventListener('click', () => {
    const prevIndex = (currentIndex - 1 + slideCount) % slideCount;
    switchSlide(prevIndex);
    resetTimer();
  });

  nextBtn.addEventListener('click', () => {
    const nextIndex = (currentIndex + 1) % slideCount;
    switchSlide(nextIndex);
    resetTimer();
  });

  // 鼠标移入暂停轮播，移出继续
  sliderWrapper.addEventListener('mouseenter', () => {
    clearInterval(timer);
  });
  sliderWrapper.addEventListener('mouseleave', () => {
    autoPlay();
  });
}

// 重置轮播定时器
function resetTimer() {
  clearInterval(timer);
  autoPlay();
}

// 初始化执行
initPagination();
autoPlay();
initEventListeners();
handleSlideExit();