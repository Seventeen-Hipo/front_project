// 1. 海洋动物卡片滚动渐入效果
const oceanCards = document.querySelectorAll('.card');
const intersectionObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('reveal');
    }
  });
}, { threshold: 0.15 });

// 监听所有卡片元素
oceanCards.forEach(card => intersectionObserver.observe(card));

// 导航状态交由 global_nav.js 处理