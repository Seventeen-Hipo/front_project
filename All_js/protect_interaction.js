const revealTargets = document.querySelectorAll('.box, .mission-card, .impact-card');
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('reveal');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.18 });

revealTargets.forEach(target => observer.observe(target));
// 导航状态交由 global_nav.js 处理