
(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const stages = document.querySelectorAll('.nfig');
  function play(stage) {
    const nodes = stage.querySelectorAll('.a-draw, .a-pop, .a-rise');
    stage.classList.remove('is-playing');
    nodes.forEach(node => { node.style.animation = 'none'; });
    void stage.offsetWidth;
    nodes.forEach(node => { node.style.animation = ''; });
    stage.classList.add('is-playing');
  }
  stages.forEach(stage => {
    stage.querySelectorAll('.a-draw').forEach(path => {
      if (!path.style.getPropertyValue('--len')) {
        path.style.setProperty('--len', Math.ceil(path.getTotalLength() + 2));
      }
    });
    stage.classList.add('is-animated');
    stage.querySelector('.replay')?.addEventListener('click', () => play(stage));
  });
  if (reduced || !('IntersectionObserver' in window)) {
    stages.forEach(play);
  } else {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) { play(entry.target); observer.unobserve(entry.target); }
      });
    }, {threshold:0.25, rootMargin:'0px 0px -8% 0px'});
    stages.forEach(stage => observer.observe(stage));
  }
})();
