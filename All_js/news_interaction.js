// 1. 资讯项滚动渐入效果
const newsRows = document.querySelectorAll('.row');
const intersectionObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('reveal');
    }
  });
}, { threshold: 0.15 });

// 监听所有资讯项
newsRows.forEach(row => intersectionObserver.observe(row));

// 导航状态交由 global_nav.js 处理