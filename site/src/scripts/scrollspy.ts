// Table of contents: the current entry is the last section whose top has passed min(a third of the viewport, 100px); the first section by default.
// Navigation, not animation: runs under reduced motion too.
const sections = [...document.querySelectorAll<HTMLElement>('.prose > section[id]')];
const links = [...document.querySelectorAll<HTMLAnchorElement>('.toc a[href^="#"]')];

function spy() {
  const line = Math.min(innerHeight / 3, 100);
  const current = sections.filter((s) => s.getBoundingClientRect().top <= line).at(-1)?.id ?? sections[0]?.id;
  for (const a of links) {
    if (a.getAttribute('href') === `#${current}`) a.setAttribute('aria-current', 'true');
    else a.removeAttribute('aria-current');
  }
}
addEventListener('scroll', spy, { passive: true });
addEventListener('resize', spy);
spy();
