// Table of contents: the current entry is the last section whose top has passed a third of the viewport.
// Navigation, not animation: runs under reduced motion too.
const sections = [...document.querySelectorAll<HTMLElement>('.prose > section[id]')];
const links = [...document.querySelectorAll<HTMLAnchorElement>('.toc a[href^="#"]')];

function spy() {
  const line = innerHeight / 3;
  const current = sections.filter((s) => s.getBoundingClientRect().top <= line).at(-1)?.id;
  for (const a of links) {
    if (a.getAttribute('href') === `#${current}`) a.setAttribute('aria-current', 'true');
    else a.removeAttribute('aria-current');
  }
}
addEventListener('scroll', spy, { passive: true });
addEventListener('resize', spy);
spy();
