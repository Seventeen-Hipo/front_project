// 元素滚动渐入效果
const blocks = document.querySelectorAll('.block');
const intersectionObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('reveal');
    }
  });
}, { threshold: 0.15 });

blocks.forEach(block => intersectionObserver.observe(block));

// 导航状态交由 global_nav.js 处理