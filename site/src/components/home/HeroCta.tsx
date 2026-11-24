import type { ReactNode } from 'react';
import ClickSpark from '../reactbits/ClickSpark';
import StarBorder from '../reactbits/StarBorder';

const SPARKS = ['#f3dfa2', '#b8913a'];

// Main call to action: a gold star circles the button, gold sparks on click.
export default function HeroCta({ href, children }: { href: string; children?: ReactNode }) {
  return (
    <ClickSpark className="cta" style={{ width: 'auto', height: 'auto' }} sparkColor={SPARKS} sparkSize={12} sparkRadius={26} duration={600}>
      <StarBorder as="a" href={href} className="btn-ivy" color="#e6cc85" trailColor="#a8842f" duration={5} thickness={1.5} radius={4} glow={0.35} hover="none" clickPulse={false} borderColor="transparent">
        {children}
      </StarBorder>
    </ClickSpark>
  );
}
