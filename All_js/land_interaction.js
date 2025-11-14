// 1. 陆地动物卡片滚动渐入效果
const landCards = document.querySelectorAll('.card');
const intersectionObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('reveal');
    }
  });
}, { threshold: 0.15 });

// 监听所有卡片元素
landCards.forEach(card => intersectionObserver.observe(card));

// 导航状态交由 global_nav.js 处理