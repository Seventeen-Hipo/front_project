// 鸟类卡片滚动渐入效果
const birdCards = document.querySelectorAll('.card');
const intersectionObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('reveal');
    }
  });
}, { threshold: 0.15 });

// 监听所有卡片元素
birdCards.forEach(card => intersectionObserver.observe(card));

// 导航状态交由 global_nav.js 处理