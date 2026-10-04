/** The value of a color token from theme.css. GSAP does not interpolate `var(--...)`, so color animations use this function. */
export function token(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}
