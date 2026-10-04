/**
 * The order of the slides. A new slide: a file `src/slides/<id>.js`, an import here, its words under
 * `slides.<id>` in both content files and its time in `src/slides/timing.js` (MODULE.md, section Main records and contracts).
 */

import title from './title.js';
import problem from './problem.js';
import solution from './solution.js';
import states from './states.js';
import facts from './facts.js';
import demo from './demo.js';
import data from './data.js';
import architecture from './architecture.js';
import business from './business.js';
import status from './status.js';

export const slides = [title, problem, solution, states, facts, demo, data, architecture, business, status];
