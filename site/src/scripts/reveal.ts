// Each section plays its animations once, when ~20 % of it is on screen. Without IntersectionObserver,
// or under reduced motion, the page is never armed and nothing is paused.

// A section 5 roots tall or more may never be 20 % visible: it reveals as soon as it shows.
export const shouldReveal = (e: IntersectionObserverEntry) =>
  e.isIntersecting && (e.intersectionRatio >= 0.2 || e.boundingClientRect.height * 0.2 >= (e.rootBounds?.height ?? 0));

if ('IntersectionObserver' in globalThis && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!shouldReveal(e)) continue;
      e.target.classList.add('in');
      io.unobserve(e.target);
    }
  }, { threshold: [0, 0.2], rootMargin: '0px 0px -10% 0px' });
  document.querySelectorAll('[data-reveal]').forEach((el) => io.observe(el));
  document.documentElement.classList.add('armed');
}
