/* Node test for the read-along player's pure active-word search (LGA-47).
 * No jsdom needed — activeIndex is DOM-free. Run: node lingua/static/lingua/readalong.test.js
 */
"use strict";
var assert = require("assert");
var _mod = require("./readalong.js");
var activeIndex = _mod.activeIndex;
var sentenceParities = _mod.sentenceParities;

var W = [
  { i: 0, s_ms: 0, e_ms: 300 },
  { i: 1, s_ms: 300, e_ms: 600 },
  { i: 2, s_ms: 600, e_ms: 900 },
];

// before the first word
assert.strictEqual(activeIndex(W, -10, -1), -1, "before start -> -1");
// forward advance (fast path)
assert.strictEqual(activeIndex(W, 0, -1), 0, "at 0 -> word 0");
assert.strictEqual(activeIndex(W, 350, 0), 1, "forward hint cursor 0 -> word 1");
assert.strictEqual(activeIndex(W, 650, 1), 2, "forward hint cursor 1 -> word 2");
// backward jump (tap-to-seek earlier) -> binary search finds it, no skipping
assert.strictEqual(activeIndex(W, 50, 2), 0, "backward jump -> word 0");
// discontinuous forward jump (seek ahead) past the fast path
assert.strictEqual(activeIndex(W, 650, 0), 2, "discontinuous forward -> word 2");
// exactly on a boundary belongs to the later word
assert.strictEqual(activeIndex(W, 300, 0), 1, "boundary 300 -> word 1");
// past the end -> last word stays active
assert.strictEqual(activeIndex(W, 5000, 2), 2, "past end -> last word");
// empty timing array never throws
assert.strictEqual(activeIndex([], 100, -1), -1, "empty -> -1");
// a stale/out-of-range cursor still resolves via binary search
assert.strictEqual(activeIndex(W, 350, 99), 1, "out-of-range cursor -> binary search");

// --- sentenceParities (shared-reading turns, LGA-74) ---
// "Hola. Soy Ana. Corro." -> sentence 0: [Hola.], sentence 1: [Soy, Ana.], sentence 2: [Corro.]
assert.deepStrictEqual(
  sentenceParities(["Hola.", "Soy", "Ana.", "Corro."]),
  ["s0", "s1", "s1", "s0"],
  "parity flips after each sentence-ending word"
);
// no sentence enders -> all one parity
assert.deepStrictEqual(sentenceParities(["uno", "dos", "tres"]), ["s0", "s0", "s0"],
  "no enders -> all s0");
// trailing closing quote after the period still ends the sentence
assert.deepStrictEqual(sentenceParities(['dijo."', "Luego"]), ["s0", "s1"],
  "punctuation + closing quote ends the sentence");
// ¿? question marks split too
assert.deepStrictEqual(sentenceParities(["¿Qué?", "Nada."]), ["s0", "s1"], "question ends a sentence");
assert.deepStrictEqual(sentenceParities([]), [], "empty -> empty");

console.log("readalong.js: all " + 15 + " player-logic assertions passed");
