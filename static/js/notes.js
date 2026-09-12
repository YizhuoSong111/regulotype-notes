// Make wide tables discoverable on small screens; content works without JS.
document.querySelectorAll('.table-scroll').forEach(region => {
  const update = () => {
    region.dataset.overflow = String(region.scrollWidth > region.clientWidth + 1);
  };
  update();
  if ('ResizeObserver' in window) new ResizeObserver(update).observe(region);
});
