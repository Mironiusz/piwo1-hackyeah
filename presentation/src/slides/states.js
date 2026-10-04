import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';
import { routeStates } from '../components/route-states.js';
import './states.css';

const t = slideText('states');
const brand = slideText('title').heading;

/**
 * The four segment states on one route, each with its name under its segment, then the rule that missing data is
 * never shown as accessible, then the same route in grayscale to prove the states do not depend on color.
 */
export default {
  id: 'states',
  summary: t.summary,
  html: `
    <p class="brand">${brand}</p>
    <h2 class="slide-title">${t.heading}</h2>
    <div class="sheet">
      <svg class="states-route" viewBox="0 0 1600 230" role="img" aria-label="${t.legend.map((l) => l.label).join(', ')}">${routeStates({ x: 130, y: 184, width: 1340 })}</svg>
      <ul class="legend">${t.legend.map((l) => `<li>${l.label}</li>`).join('')}</ul>
      <div class="states-proof">
        <div class="states-gray">
          <svg class="states-route-gray" viewBox="0 0 680 100" aria-hidden="true">${routeStates({ x: 44, y: 58, width: 590, size: 'small' })}</svg>
          <p class="states-gray-label">${t.grayscale}</p>
        </div>
        <p class="note states-channels">${t.channels}</p>
      </div>
    </div>
    <p class="plate states-rule">${t.rule}</p>`,
  notes: t.notes,

  animate(root) {
    const rule = root.querySelector('.states-rule');
    const proof = root.querySelector('.states-proof');
    gsap.set(rule, { opacity: 0, y: -18 });
    gsap.set(proof, { opacity: 0 });
    return [
      (tl) => {
        tl.from(root.querySelector('.slide-title'), { opacity: 0, y: 24, duration: 0.5, ease: 'power3.out' });
        tl.from(root.querySelector('.sheet'), { y: 110, duration: 0.6, ease: 'power3.out' }, '-=0.3');
        tl.from(root.querySelectorAll('.states-route .rs-seg'), { opacity: 0, duration: 0.35, stagger: 0.2 }, '-=0.2');
        tl.from(root.querySelectorAll('.legend li'), { opacity: 0, y: 12, duration: 0.3, stagger: 0.2 }, '<');
      },
      (tl) => {
        tl.to(rule, { opacity: 1, y: 0, duration: 0.5, ease: 'back.out(1.6)' });
      },
      (tl) => {
        tl.to(proof, { opacity: 1, duration: 0.5 });
      },
    ];
  },
};
