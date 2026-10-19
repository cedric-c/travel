/* Progressive loading for photo-heavy journal entries. */
(() => {
  const images = Array.from(document.querySelectorAll('.post-content img'));
  if (!images.length) return;

  // Make the opening photos available immediately, without fetching the whole post.
  images.slice(0, 2).forEach((img, index) => {
    img.loading = 'eager';
    if (index === 0) img.fetchPriority = 'high';
  });

  const upcoming = images.slice(2).filter((img) => img.loading === 'lazy');
  if (!('IntersectionObserver' in window)) {
    // Native lazy loading remains the fallback on older browsers.
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const img = entry.target;
      img.loading = 'eager';
      observer.unobserve(img);
    });
  }, { rootMargin: '1600px 0px', threshold: 0 });
  upcoming.forEach((img) => observer.observe(img));
})();
