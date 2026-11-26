import { useState } from 'react';
import { useReducedMotion } from 'motion/react';
import BlurText from '../reactbits/BlurText';
import RotatingText from '../reactbits/RotatingText';

const WORDS = ['API', 'app', 'bot', 'site'];
// Module-level so BlurText keeps the same targets across renders and never replays.
const FROM = { filter: 'blur(10px)', opacity: 0, y: 20 };
const TO = [{ filter: 'blur(0px)', opacity: 1, y: 0 }];
const EASE = [0.2, 0.7, 0.2, 1] as const;

// Two passes over the words (8 changes), then rest on "API".
function Rotating() {
  const reduce = useReducedMotion();
  const [changes, setChanges] = useState(0);
  return (
    <span className="rot">
      {WORDS.map((w) => <span key={w} className="rot-ghost" aria-hidden="true">{w}</span>)}
      <RotatingText
        texts={WORDS}
        splitBy="words"
        auto={!reduce && changes < 8}
        rotationInterval={2400}
        initial={{ y: '80%', opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: '-80%', opacity: 0 }}
        transition={{ duration: 0.6, ease: [0.2, 0.8, 0.2, 1], opacity: { duration: 0.45, ease: 'easeOut' } }}
        animatePresenceMode="sync"
        onNext={() => setChanges((n) => n + 1)}
      />
    </span>
  );
}

// The h1 around this island carries the accessible name.
export default function HeroTitle() {
  return (
    <BlurText
      className="ht"
      text="Mets ton API parmi les étoiles"
      delay={100}
      stepDuration={0.9}
      animationFrom={FROM}
      animationTo={TO}
      easing={EASE}
      renderWord={(word, i) => (i === 2 ? <><Rotating />{' '}</> : word)}
    />
  );
}
