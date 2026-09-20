import assert from 'node:assert/strict';
import fs from 'node:fs';

global.window = {
  matchMedia(query) {
    assert.equal(query, '(prefers-reduced-motion: reduce)');
    return { matches:true };
  },
};

await import('../world-map/3d-motion.js');
const motion = window.__potatoAtlasMotion;
assert.ok(motion, 'shared motion policy must publish an API');
assert.equal(motion.prefersReducedMotion(), true);
assert.deepEqual(
  motion.options({ duration:900, pitch:48 }),
  { duration:0, pitch:48, animate:false, essential:false },
  'reduced motion must preserve camera destination while removing animation',
);

const fake = {
  ease:null, fit:null,
  easeTo(options) { this.ease = options; },
  fitBounds(bounds, options) { this.fit = { bounds, options }; },
};
motion.easeTo(fake, { center:[1,2], duration:650 });
assert.equal(fake.ease.duration, 0);
assert.deepEqual(fake.ease.center, [1,2]);
motion.fitBounds(fake, [[0,0],[1,1]], { duration:550, maxZoom:4.8 });
assert.equal(fake.fit.options.duration, 0);
assert.equal(fake.fit.options.maxZoom, 4.8);

const read = name => fs.readFileSync(new URL(`../world-map/${name}`, import.meta.url), 'utf8');
const hover = read('3d-hover.js');
assert.ok(
  hover.indexOf("await import(versionedModule('./3d-motion.js'))") <
  hover.indexOf("await import(versionedModule('./3d-app.js'))"),
  'motion policy must load before the core app',
);

for (const name of [
  '3d-app.js',
  '3d-places.js',
  '3d-subdivisions.js',
  '3d-adl-heat.js',
  '3d-mud-below-us.js',
  '3d-axis.js',
  '3d-axis-depth.js',
  '3d-symbolic-operators.js',
]) {
  const source = read(name);
  assert.ok(source.includes('__potatoAtlasMotion') || source.includes('motion.'), `${name} must consume shared motion policy`);
}

const html = fs.readFileSync(new URL('../world-map/index.html', import.meta.url), 'utf8');
assert.ok(html.includes('@media(prefers-reduced-motion:reduce)'), 'World Map CSS must disable decorative transitions for reduced motion');

console.log('WORLD MAP REDUCED MOTION REGRESSION PASSED');
