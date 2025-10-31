// 科普分类：滚动到视口时逐个显现，并在悬停时有细致动画（见 CSS）
(function initCategoryRevealOnScroll() {
  const grid = document.querySelector('.category-grid');
  if (!grid) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        grid.classList.add('revealed');
        io.disconnect();
      }
    });
  }, { root: null, threshold: 0.15 });
  io.observe(grid);
})();
// 获取DOM元素
const sliderWrapper = document.querySelector('.slider-wrapper');
const sliderItems = document.querySelectorAll('.slider-item');
const pagination = document.querySelector('.pagination');
const prevBtn = document.querySelector('.prev-btn');
const nextBtn = document.querySelector('.next-btn');
const headerEl = document.querySelector('.header');
const sliderContainer = document.querySelector('.slider-container');
const newsSection = document.querySelector('.news-section');

// 轮播图状态
let currentIndex = 0;
const slideCount = sliderItems.length;
let timer = null;
let sliderHeight = 0;
let isAutoScrolling = false; // 动画滚动锁，避免重复触发
let headerHeight = 0;

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
  }, 3000); // 5秒切换一次
}

// 计算并更新轮播高度
function updateSliderHeight() {
  if (!sliderContainer) return;
  sliderHeight = sliderContainer.getBoundingClientRect().height || window.innerHeight;
  headerHeight = headerEl ? headerEl.getBoundingClientRect().height : 0;
  // 暴露给样式用于锚点滚动的顶部留白
  document.documentElement.style.setProperty('--header-h', `${Math.round(headerHeight)}px`);
}

// 更新导航栏透明/白底状态
function updateHeaderState() {
  const scrollTop = window.scrollY || document.documentElement.scrollTop;
  const progress = Math.min(1, Math.max(0, scrollTop / Math.max(1, sliderHeight)));

  // 背景渐变：在前 60% 距离内平滑淡入白底
  const bgAlpha = Math.min(1, progress / 0.6);

  // 在未完全退出全屏前保持 transparent 类，但用透明度做背景渐入
  if (progress < 0.98) {
    headerEl.classList.add('transparent');
    headerEl.classList.remove('solid');
    headerEl.classList.toggle('compact', progress > 0.2);
    headerEl.classList.remove('scrolled');
    headerEl.style.backgroundColor = `rgba(255,255,255, ${bgAlpha * 0.92})`;
  } else {
    // 退出全屏，切换到白底，并根据更深的滚动添加阴影
    headerEl.classList.remove('transparent');
    headerEl.classList.add('solid');
    headerEl.classList.toggle('compact', true);
    headerEl.style.backgroundColor = '';
    if (scrollTop > sliderHeight + 20) {
      headerEl.classList.add('scrolled');
    } else {
      headerEl.classList.remove('scrolled');
    }
  }

  // 轮播容器的淡出与缩放（丝滑退出全屏）
  // 轻微上移与缩放，营造沉浸式收起效果
  const scale = 1 - progress * 0.04; // 最多缩小 4%
  const translateY = progress * 16; // 轻微上移 16px
  const opacity = 1 - progress * 0.15; // 最多淡出 15%
  if (sliderContainer) {
    sliderContainer.style.opacity = `${opacity}`;
    sliderWrapper.style.transform = `translateX(-${currentIndex * 100}%) translateY(${translateY}px) scale(${scale})`;
    // 分割过渡：底部白色圆角盖板高度随进度增加
    const dividerH = Math.round(progress * 140); // 盖板高度 0-140px
    sliderContainer.style.setProperty('--divider-h', `${dividerH}px`);
  }

  // 正文容器轻微上移与阴影渐入，制造“承接”感
  const contentLift = Math.round(Math.min(32, progress * 48)) * -1; // 上移最多 -32px
  const content = document.querySelector('.container');
  if (content) {
    content.style.setProperty('--content-lift', `${contentLift}px`);
  }
}

// 平滑退出全屏轮播（滚轮或上滑手势）
function enableFullscreenExit() {
  if (!sliderContainer) return;

  // 鼠标滚轮下滑退出（仅在顶端区域生效）
  window.addEventListener('wheel', (e) => {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    if (!isAutoScrolling && scrollTop < 10 && e.deltaY > 0) {
      e.preventDefault();
      scrollToBelowSlider(520);
      return;
    }

    // 在接近分割线位置，向上滚进入全屏
    const nearDividerTop = Math.abs(scrollTop - sliderHeight) < 80;
    if (!isAutoScrolling && nearDividerTop && e.deltaY < 0) {
      e.preventDefault();
      smoothScrollTo(0, 520);
      return;
    }
  }, { passive: false });

  // 触摸上滑退出（移动端）
  let touchStartY = 0;
  sliderContainer.addEventListener('touchstart', (e) => {
    touchStartY = e.touches[0].clientY;
  }, { passive: true });
  sliderContainer.addEventListener('touchend', (e) => {
    const endY = e.changedTouches[0].clientY;
    const deltaY = endY - touchStartY; // 上滑为负
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    if (!isAutoScrolling && scrollTop < 10 && deltaY < -30) {
      scrollToBelowSlider(520);
    }
  }, { passive: true });

  // 内容区域手势：在接近分割线时下滑（手指向下，deltaY>阈值）回到全屏
  let pageTouchStartY = 0;
  document.addEventListener('touchstart', (e) => {
    pageTouchStartY = e.touches[0].clientY;
  }, { passive: true });
  document.addEventListener('touchend', (e) => {
    const endY = e.changedTouches[0].clientY;
    const deltaY = endY - pageTouchStartY; // 下滑为正
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const nearDividerTop = Math.abs(scrollTop - sliderHeight) < 60;
    if (!isAutoScrolling && nearDividerTop && deltaY > 40) {
      smoothScrollTo(0, 520);
    }
  }, { passive: true });
}

// 滚动到轮播图下方，考虑固定导航的高度，避免遮挡标题
function scrollToBelowSlider(duration = 520) {
  const currentScroll = window.scrollY || document.documentElement.scrollTop;
  const headerH = (headerEl ? headerEl.getBoundingClientRect().height : 0);
  const extra = 24; // 额外缓冲
  // 优先滚到“动物新闻”标题上方，减去导航栏高度与缓冲，确保不被遮挡
  if (newsSection) {
    const newsTop = newsSection.getBoundingClientRect().top + currentScroll;
    const targetTop = Math.max(0, newsTop - headerH - extra);
    smoothScrollTo(targetTop, duration);
  } else {
    // 兜底：按轮播高度偏移
    const target = sliderHeight + headerH + extra;
    smoothScrollTo(target, duration);
  }
}

// 自定义缓动滚动，获得更丝滑的效果
function smoothScrollTo(targetTop, duration = 480) {
  const startTop = window.scrollY || document.documentElement.scrollTop;
  const distance = targetTop - startTop;
  if (Math.abs(distance) < 1) return;
  const startTime = performance.now();

  // easeOutCubic
  const ease = (t) => 1 - Math.pow(1 - t, 3);

  isAutoScrolling = true;
  function step(now) {
    const elapsed = now - startTime;
    const t = Math.min(1, elapsed / duration);
    const eased = ease(t);
    const current = startTop + distance * eased;
    window.scrollTo(0, current);
    if (t < 1) {
      requestAnimationFrame(step);
    } else {
      // 结束后更新状态与样式
      isAutoScrolling = false;
      updateHeaderState();
    }
  }

  requestAnimationFrame(step);
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

  // 滚动时更新导航栏状态
  window.addEventListener('scroll', updateHeaderState, { passive: true });
  window.addEventListener('resize', () => {
    updateSliderHeight();
    updateHeaderState();
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
updateSliderHeight();
updateHeaderState();
initEventListeners();
enableFullscreenExit();

// 动物新闻专栏：克隆内容以实现无缝滚动
(function initNewsMarquee() {
  const marquee = document.getElementById('newsMarquee');
  if (!marquee) return;
  const track = marquee.querySelector('.news-track');
  if (!track) return;
  // 若子元素不足以铺满两屏，克隆一次以保证 -50% 平移时无缝
  const items = Array.from(track.children);
  const clone = document.createDocumentFragment();
  items.forEach((el) => clone.appendChild(el.cloneNode(true)));
  track.appendChild(clone);

  // 触摸滑动：滑动时暂时暂停动画，提升可控性
  let touchStartX = 0;
  marquee.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
    track.style.animationPlayState = 'paused';
  }, { passive: true });
  marquee.addEventListener('touchend', (e) => {
    const dx = e.changedTouches[0].clientX - touchStartX;
    // 根据滑动方向，瞬时偏移一点点，营造跟手感（随后动画继续）
    const current = getComputedStyle(track).transform;
    // 简化处理：不解析矩阵，恢复动画即可
    track.style.animationPlayState = 'running';
  }, { passive: true });
})();