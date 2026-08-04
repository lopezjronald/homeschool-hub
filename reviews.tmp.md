##### LESSON 74 #####
## Verification run

```
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
....................
----------------------------------------------------------------------
Ran 20 tests in 0.649s

OK
Destroying test database for alias 'default'...
Found 20 test(s).
System check identified no issues (0 silenced).
```

## Arithmetic recomputation (all pass)

| lesson claim | source | recomputed |
|---|---|---|
| `4 × 1,000 = 4,000` (:162) | src:46 `4 × 1,000 = 4,000 fish` | 4000 ✓ |
| `4,000 - 1,000 = 3,000` (:167) | src:61 `4,000 - 1,000 = 3,000` | 3000 ✓ |
| `6,000 - 5,000 = 1,000` (:184) | src:75 `6,000-5,000 = 1,000` | 1000 ✓ |
| `Δy = 6,000 - 1,000 = 5,000` (:285) | src:103 identical | 5000 ✓ |
| `Δx = 5 - 1 = 4` (:289) | src:104 identical | 4 ✓ |
| `5,000 / 4 = 1,250` (:293, :298) | src:106 `∆y/∆x = 5,000/4 = 1,250` | 1250 ✓ |
| `3 × 100,000 + 50,000 = 350,000` (:327) | src:112 `Half an airplane = 50,000` | 350000 ✓ |
| `2,000 / 2 = 1,000` (:345) | src:58-59 | 1000 ✓ |
| `Using 5 gives 1,000 fish/month` (:340) | — | 5000/5=1000 ✓ |
| parent shares 5.6/11.1/22.2/27.8/33.3 (:389-395) | src:83 `33.3%` | sum = 100.0 ✓, matches widget's `toFixed(1)` output exactly (verified via node) |
| November ≈ 7,250 (:470) | — | 6000+1250 ✓ |

Method fidelity on 74.1/74.2/74.3/74.5 is exact — the STEPPER (:269-295) reproduces Saxon's four moves in Saxon's order, including src:99 "the two points farthest apart" → :278 "Farthest apart is best".

---

## Findings

### HIGH — the bar graph the lesson describes is not the bar graph it draws
`seed_saxon_74.py:163-167` tells her:

> "August lands exactly on a line: 4,000. June does not — it sits about **halfway between 0 and 2,000**"

and `:345` repeats it as the *right* line of an errors block: `"June sits halfway from 0 to 2,000 → 2,000 / 2 = 1,000 fish"`.

Both sentences are true of Saxon's printed graph (src:58 "It is obviously between 0 and 2,000"). Neither is true of the widget she is looking at. `static/js/portal-chart.js:186` calls `ticks(max, 5)` with `niceMax([1000..6000]) = 6000`, so the gridlines are **0 / 1.2k / 2.4k / 3.6k / 4.8k / 6k**. Confirmed by running the module, and pinned as intended behaviour by `static/js/portal-chart.test.js:26`:

```
check("gridlines run from 0 to the top", C.ticks(6000, 5), [0, 1200, 2400, 3600, 4800, 6000]);
```

There is no 4,000 line for August to "land exactly on" and no 2,000 line for June to sit halfway below. `portal-chart.js:26` states the opposite intent in its own comment — "so the gridlines land on numbers a child can read (2,000 / 4,000 / 6,000)" — which `ticks(max, 5)` does not deliver (`ticks(6000, 3)` would). This lands on the exact habit the lesson makes its headline (`:127-132` "Find the key or the scale FIRST"): she is told to check the scale, checks it, and the scale contradicts the worked example. Not a wrong answer — a dead end, which is the failure mode this review exists to catch.

### MEDIUM — the scatterplot is not renamed to Month 1–5, but the lesson says it is
Src:96-97: "Notice also we changed from the name of the month to a number." `seed_saxon_74.py:274-276` faithfully repeats this — "June, July, August, September, October **became Month 1, 2, 3, 4, 5**" — and `:281` has her write `(1, 1,000) and (5, 6,000)`. But `portal-chart.js:249` (`drawScatter` → `xLabels`) prints `labels[i]`, i.e. **June / July / Aug / Sept / Oct**. The one chart whose axis relabelling Saxon calls out by name is the one that doesn't do it, and `:229`'s translation row `"(5, 6000) is October"` has no 5 on the page to point at.

### MEDIUM — 74.4 leads with a method Saxon doesn't use and the pie graph can't supply
Saxon (src:83-84): *"Observing the graph, we see 33.3% of the fish were caught in October. 33.3% is basically 1/3, so October is the correct month."* — read the label, recognise the fraction. Done.

`seed_saxon_74.py:185-190` inverts this: it leads with *"The whole is all 18,000 fish. One third of 18,000 is 6,000, and 6,000 is October,"* and only then offers *"Read the other way round"* for Saxon's actual route. The math line is `6,000 / 18,000 = 1 / 3 = 33.3% → October`. On her DIVE practice set she gets a pie chart with percentage labels and **no total** — the primary path taught here needs a number the chart does not carry (and which Saxon never prints). Saxon's method should lead; the total-based check is the aside.

Sub-nit at the same line: `1 / 3 = 33.3%` is asserted as exact. It isn't (33.3% = 333/1000). The lesson's own prose two lines later gets this right — "33.3% is **basically** one third" — matching src:84.

### MEDIUM — July = 2,000 and the 18,000 total are derived, but presented to her unhedged
The module docstring (`:16-21`) is honest: *"July is never stated in words — it lives only in a figure this file cannot see. It is RECOVERED, not invented."* The derivation is sound and uniquely determined (if July were 3,000 the total is 19,000 and October reads 31.6%, not the src:83 33.3%). But nothing child-facing carries that hedge: `:64-66`, `:119-122` ("All five months together come to **18,000 fish**") and the parent table `:388-395` all state it flat. If the DIVE figure's July bar differs, her page and her book disagree with no signal that one of them was reconstructed. The parent guide is the natural place for a one-line note; it has none.

### MEDIUM — "3½ planes" is an invented figure attached to a real practice problem
`:326-330`: *"Practice problem 1 has exactly this shape: whole planes are 100,000 tourists each, so half a plane is 50,000."* The key and the half-value are verbatim from src:112-114. The **3½** is not — src:118 shows February only as a figure. The arithmetic is right, but a 12-year-old reading "practice problem 1 has exactly this shape" directly above `= 350,000 tourists` may transcribe 350,000 as the answer to 174. The word "shape" is doing more load-bearing work than it can hold at that distance.

### MEDIUM — "histogram" never appears in the student content
Src:14-15 defines it: *"a bar graph, also referred to as a histogram."* Her practice set uses the word as the operative term in problem 13 (src:177 "Which of the following is a correct **histogram** of the coin data"). The chart-comparison table (`:199-211`) says only "bar graph"; the synonym survives solely in the parent guide (`:485`).

### LOW — Saxon's `chart` definition and the chart/instrument contrast are dropped
Src:11-13 defines chart as covering *"tables, graphs, and diagrams"*; the masthead reduces it to `"chart = a picture of numbers"` (`:50`) and the table (`:198-211`) lists only the five graph types. Src:27-31's contrast — a speedometer *measures, records and represents*, so it is an **instrument**; *"A chart's only job is to represent data"* — is absent, though `:47-49`'s thesis ("A chart does not *contain* the data — it **represents** it") is a fair paraphrase of the same idea.

### LOW — errors item 4's wrong/right lines aren't parallel
`:337-339`: wrong is `"Months 1 to 5, so Δx = 5"`, right is `"Δy / Δx = 5,000 / 4 = 1,250"`. Both are correct as written, but the right line never states the corrected claim (`Δx = 4`) that the wrong line got wrong; it jumps a step. The note (`:341-342`) recovers it. Cosmetic, in the highest-authority block.

### LOW — pictograph key renders without the thousands comma
`portal-chart.js:291` builds `"one block = " + per + " " + unit` → **"one block = 1000 fish"**, while every text reference (`:157`, `:224-226`) writes it as **"1,000 fish"** and src:37 uses `= 1,000 fish`.

## Cleared
- **Condescension / hand-waving (check 6):** none found. The hard step is Δx = gaps-not-dots, and it is slowed down three separate times (`:287-288`, `:337-342`, `:362`) — the opposite of hand-waving. `:264-265`'s "pick the two points farthest apart" is Saxon's own reasoning (src:99), not filler.
- **Errors block (check 5):** all five `wrong` lines are genuinely wrong and all five `right` lines genuinely right; recomputed individually above.
- **Parent script (check 7):** `:404-428` is sayable verbatim and teaches Saxon's method, including the literal words for the run — *"make her count the jumps, not the dots"* (4, not 5) — and the `y = mx + b` connection Saxon leaves implicit. Step 4's *"How many fish is that?"* correctly forces share→count. Step 1's five numbers are readable aloud as written.
- **Widget/config validity:** all 14 `KIND_*` constants exist (`tutor/models.py:242-255`); the `chart` widget supports every key passed — `kinds`, `per`, `unit`, `trend`, `label` (`portal-chart.js:167-335`). `trend` correctly draws first-to-last dot, and the intermediate points are genuinely off that line (month 2: 2,000 actual vs 2,250 on-trend), so src:95 *"The points don't exactly follow a line"* is true of the rendered figure.
- **Review-lesson attribution:** `:483-486` matches src:8 (`Review: Lessons 51, 65, 68, 70`) with 51→coordinate plane (src:52) and 68→plotting linear equations (src:94) both sourced correctly.

**Verdict: NEEDS WORK**
##### LESSON 75 #####
## Verification method

Every numeric claim in the authored lesson was recomputed independently (Python, shown below) and matched line-by-line against the source. Full binary table 1–20 regenerated with `format(n,'b')` and compared row by row.

```
5568*3712 = 20668416 → 20.668416 → 20.7
1600*1200 = 1920000  → 1.92
4032*3024 = 12192768 → 12.2
2**20     = 1048576
1+2+4+8+16 = 31
binary 1..20 = 1,10,11,100,101,110,111,1000,1001,1010,1011,1100,1101,1110,1111,10000,10001,10010,10011,10100
```

## 1. Numbers — CLEAN

- `seed_saxon_75.py:123` `"1(8) + 0(4) + 1(2) + 1(1) = 8 + 2 + 1 = 11"` vs source `lesson_075.txt:82` `1(8) + 0(4) + 1(2) + 1(1) = 8 + 2 + 1 = 11.` — character-for-character.
- `:126` `"1(8) + 0(4) + 0(2) + 1(1) = 8 + 1 = 9"` vs source `:88` — identical.
- `:130` `"1(16) + 0(8) + 0(4) + 1(2) + 1(1) = 16 + 2 + 1 = 19"` vs source `:93` `1(16)+0(8) + 0(4) + 1(2) + 1(1) = 16 + 2 + 1 = 19.` — identical.
- `:300,:305,:309` `5568 × 3712 = 20,668,416` → `÷ 1,000,000 = 20.668416` → `20.7` vs source `:153` `5568 x 3712 = 20,668,416 pixels = 20.668416 = 20.7 MP`. Recomputed: exact. The authored version is *better* than the source, which sloppily writes `20,668,416 pixels = 20.668416` with no divide shown; `:305` supplies the missing `÷ 1,000,000`.
- `:315` `1600 × 1200 = 1,920,000 pixels → 1.92 MP` vs source `:140,143`. Exact.
- `:232` `2^20 = 1,048,576` vs source `:145`. Exact.
- Table `:240-260`: all 20 rows match the source's Rules table `:16-35` in binary string, power decomposition, sum, and base-10 value. No transcription drift.
- `:325-328` reveal `10100` → `16 + 4 = 20` — correct, and matches table row `:260`.
- Parent extras, all recomputed correct: `:449-450` 13 → 1101 (greedy 8, then 4, then 1); `:445` one hand = 31; `:451-453` 4032 × 3024 = 12,192,768 → 12.2 MP.
- No invented worked example in the child-facing blocks. Both WORKED blocks are Examples 75.1 and 75.2.

## 2. Method — CLEAN

Source `:76-78`: *"place the ones and zeros in the base 2 chart. Then, if a number is 'on' (1), then multiply by the corresponding base 2 conversion. If a number is 'off' (0), ignore it because you are multiplying by 0"*.

Authored `:93-106` is that method, in that order: draw the chart → drop the digits in → cross out the zeros → add. `:102-104` explicitly names Saxon's rationale: *"Saxon says to ignore it because you are multiplying by zero — crossing it out is the same thing"*. No competing algorithm (no repeated division-by-2, no doubling method) is taught anywhere. `:150` writes the full term list including zero terms, exactly as Saxon does — so what she writes on DIVE will look like the book.

75.2 likewise: source `:151-152` *"multiply 5568 by 3712, and divide by 1 million (or move the decimal over 6 places)"* → authored `:301-305` gives both, same order.

## 3. Notation / vocabulary — CLEAN

`1 = ON, 0 = OFF` (source `:11`) drives the masthead roles `:36-39`. `1(8)`/`0(4)` term form preserved and decoded at `:186-189`. Superscript powers `2⁰…2⁴` match the source's place chart `:14`. "base 10" (not "decimal") throughout, as Saxon. `pixel = picture element` (`:276` vs source `:39`), `1 MP = 1,000,000 pixels` (`:192` vs source `:37`). Place-doubling stated as *"the number of digits always equals the base"* `:71` — Saxon's `:56-57` *"Positional base systems have a number of digits equal to the base value."*

## 4. Unseen figures — CLEAN

The source's three images (bear photos `:106`, display-settings dialog `:123`, and the practice-set graphs) are never referenced. Only two "below" references exist, `:109` and `:172`, both pointing at the KIND_TABLE block, which `_saxon_seed.py:213` orders after both (`enumerate(self.BLOCKS, start=1)` → list order is render order). The docstring `:11-15` states the omission deliberately. The one number lifted out of a figure (`1600 × 1200`) is stated in the source's body text at `:138`, not only in the screenshot.

## 5. Errors block — CLEAN

All five `wrong` lines are false and all five `right` lines are true:

| # | wrong | true? | right | true? |
|---|---|---|---|---|
|1|`1011 → one thousand and eleven`|false ✓|`1011 → 8 + 2 + 1 = 11`|true ✓|
|2|`binary 10 = ten`|false ✓|`binary 10 → 2`|true ✓|
|3|`10011 → 8 + 2 + 1 = 11`|false ✓|`10011 → 16 + 2 + 1 = 19`|true ✓|
|4|`5568 × 3712 = 20,668,416 MP`|false ✓ (unit)|`… ÷ 1,000,000 = 20.668416 → 20.7 MP`|true ✓|
|5|`1 MP = 1,000 pixels`|false ✓|`1 MP → 1,000,000 pixels`|true ✓|

Item 4 is the only subtle one — the arithmetic inside the "wrong" line is correct and only the *unit* is wrong. `:221` names it precisely (*"Multiplying the pixels and calling that the megapixels"*) and `:224` explains it, so it cannot be misread as bad multiplication.

## 6. Tone / hard step — CLEAN

The hard step (right-hand alignment, and the extra 16 place when a fifth digit appears) is hit three separate ways: `:97-100`, the whole STEPPER `:135-158`, and error 3 `:215-220`. Nothing hand-waves it. Closest thing to condescension is `:72` *"the same chart you have used since second grade"* — reads as reassurance ("you already own this"), not a put-down. Not filed.

## 7. Parent script — CLEAN, and sayable

`:382-396` is five numbered beats, each a sentence a parent can read aloud, each ending in a question with a stated target answer. It teaches Saxon's method and not another one: beat 3 builds the places right-to-left *before* the number appears; beat 4 aligns `1011` from the right and asks only "on or off?"; beat 5 uses `10011` to force the 16 place and then makes her discover the dropped-zero failure. Beat 3's *"Do not write them left to right — the order you build them in is the order she will build them in"* is a real teaching instruction, not filler.

Widget references verified against the implementation, not assumed: `static/js/portal-binary.js:136` `button("All off", …)` and `:140` `button("Count up", …)` both exist, so `:171` and `:398` do not send her looking for controls that aren't there. `config {"bits": 5, "value": 11}` → `toBits(11,5)` = `01011`, matching the comment at `:167-169`. Counting up 20 times from 0 stays inside 5 bits (max 31).

---

## Findings

**MEDIUM — `seed_saxon_75.py:343` (also `:108-111`, `:373-376`): the "every Practice Set problem" promise is broader than Saxon's, and broader than the actual practice set.**
Source `:94-97` is scoped to the binary section: *"EVERY Practice Set problem will be about one of the numbers listed in the Lesson 75 Rules"* — sitting immediately after Example 75.1, meaning every *binary-conversion* problem. Practice Set 75 (`:158-237`) has 20 problems, of which only 175 and 275 are conversions; 375 is megapixels and 474–2028 are review (Hawaii tourists, snappers, sphere volume, scientific notation). The RECAP states it unscoped — `"Stuck? Every Practice Set problem in this lesson is one of the twenty numbers in the table. Look it up — that is allowed here."` — and it is the *last* line she reads before starting the set. The STEPS version `:108` sits inside the binary section and is contextually fine; the RECAP and parent versions are not. Suggested rescope: "every binary-conversion problem in the set".

**MEDIUM — `seed_saxon_75.py:404`: the one number in the lesson that is neither in the source nor derived from it.**
Parent script: `"and something has to decide the colour of every single one, sixty times a second."` Nothing in the source states a refresh rate. The child-facing version of the same sentence, `:319`, says *"many times a second"* — correct and unsourced-safe. The page and the script disagree in specificity for no gain; `:404` should match `:319`.

**LOW — `seed_saxon_75.py:52` vs `:386`: two different phrasings of the carry boundary.**
Page: `"So a computer runs out after **two** instead of after ten"`. Parent script: `"So when does it have to start a new column?" — you want "after one."` Both describe the same event (the new column opens at two) and both lead to `10 = 2`, so neither is wrong — but she reads one and hears the other in the same sitting. The finger metaphor at `:82-84` ("hold up one finger") makes "after one" the parallel form; `:52` silently switches from counting objects to counting *states* ("Two states") to justify "after two".

**LOW — `seed_saxon_75.py:190`, `:280-281`, `:340-341`: Saxon's definition of *matrix* is softened.**
Source `:41`: *"matrix: A two-dimensional array consisting of rows and columns of numbers."* Authored renders it as `"a rectangle of rows and columns"`. The word **array** never appears in the lesson. Conceptually identical; but "array" is the term in the DIVE definition list she may be quizzed on.

**LOW — `seed_saxon_75.py:73-74`: the chart extends both ways in the source, one way here.**
Source `:71`: *"you can extend the chart to the right or left as much as needed"*, and both place charts (`:14`, `:68`) print the `2⁻¹ = 1/2` place. Authored: `"You can stretch it further left whenever you need more room."` Nothing in Practice Set 75 needs the fractional place, so this costs her nothing today — but the source chart she is looking at has a column the lesson never accounts for.

**LOW — `seed_saxon_75.py:290-312`: Example 75.2 is a calculator problem and the lesson doesn't say so.**
Source `:146` marks it `(C)`, and `:157` defines that as *"calculator use is allowed but not required."* Nothing in the WORKED block or the parent guide mentions it, so a conscientious child may grind out 5568 × 3712 by hand.

**LOW — `seed_saxon_75.py:451-453`: invented (but correct) extension example.**
`4032 × 3024` is not from the source. It is framed as *"Look up its camera resolution — something like 4032 × 3024"* in the optional Extend section, and the arithmetic checks (12,192,768 → 12.2 MP). Reporting for completeness only; it is not presented as Saxon's.

**LOW — `tutor/tests.py:1639-1663`: the arithmetic guard cannot read this lesson's signature notation.**
`_value()` normalises implicit multiplication only for `)(` (`:1657`), so `1(8) + 0(4) + 1(2) + 1(1)` raises `TypeError` inside `eval` and is discarded as `None` — that is the source of the twelve `SyntaxWarning: 'int' object is not callable` lines in the test run. The `= 8 + 2 + 1 = 11` tail is still balance-checked, so the answers are guarded; the *term list* is not. Mutating `0(4)` → `1(4)` at `:123` would leave the suite green. Not a defect in the lesson — every term list above was checked by hand instead — but the guard is thinner on Lesson 75 than the run's "OK" implies.

**Observation (not filed):** the source's young-earth aside at `:55-56` (*"standard practice in the pre-Flood world"*) is dropped from `:46-49`, which keeps only the sourced *"at least 3000 B.C."*. No mathematical consequence; flagging only because it is a deliberate divergence from a purchased DIVE lesson the family chose.

---

## Test run (verbatim)

```
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
....................
----------------------------------------------------------------------
Ran 20 tests in 0.599s

OK
Destroying test database for alias 'default'...
Found 20 test(s).
System check identified no issues (0 silenced).
```

(Lesson 75 is genuinely inside that sweep — `tutor/tests.py:1306` `saxon_lesson_numbers()` discovers seeders by globbing `seed_saxon_<n>.py`, so `seed_saxon_75.py` is picked up automatically.)

No file was edited.

FAITHFUL — every number, every worked line, and Saxon's own method and notation check out; the open items are one over-scoped promise, one unsourced "sixty times a second", and minor vocabulary trims.
##### LESSON 76 #####
## Verification against the source

**Test run (verbatim, from `C:/Users/lopez/code/django-projects/homeschool-hub`):**
```
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
[... x12 ...]
....................
----------------------------------------------------------------------
Ran 20 tests in 0.644s

OK
Destroying test database for alias 'default'...
Found 20 test(s).
System check identified no issues (0 silenced).
```

### 1. Arithmetic — every worked example recomputed by hand, all clean
- **76.1** a/b/c: `all R` / `R≥0` / `all R, R≥2` — source lines 36, 45, 53-54: `domain = range = all R`, `domain = range = R≥0`, `domain =x= all R` / `range =f(x)= R≥2`. Exact match (seed 157, 163, 169).
- **76.2a**: source 66/73 `-2≤x<4`, `-1≤f(x)<2`; seed 190/198 identical.
- **76.2b**: source 80/88 `-4<x≤4`, `0≤f(x)<5`; seed 211/217 identical. Independently checked: a V from (−4,5) hollow, down to 0, up to (4,4) filled → union of arms = [0,5). Correct.
- **76.3a**: `6ab²/b²=6a` ✓, `4a²b/ab = 4(a·ab)/ab = 4a` ✓, `3a+6a+4a=13a` ✓ (source 110-111 `3a + 6a + 4a=` … `9a + 4a = 13a`).
- **76.3b**: `−5a³b/b=−5a³` ✓, `4a³b/ab = 4(a²·ab)/ab = 4a²` ✓, `3a²+4a²−5a³ = 7a²−5a³` ✓ (source 119-120 identical).
- **Parent "Extend it"** (`seed_saxon_76.py:501`): `5x²y/xy = 5x`, `5x+3x = 8x` ✓. Author-invented but explicitly framed as an extension, and correct.
- No invented example found. Grid bounds ±6 match the established Lesson 73 widget precedent.

### 2. Method — Saxon's, not a substitute
The two-sweep reading method, "edge ⇒ forever" (source 29-30 / seed 100-102), Lesson 26 open/closed circles (source 59-60 / seed 104-106), x-vs-f(x) lettering (source 53-54 / seed 110-112) are all Saxon's own. Nothing is solved algebraically where Saxon reads.

### 3. Notation — `all R`, `R≥0`, `R≥2`, `Domain:`, `Range:`, `f(x)` all match. Vertex rule (source 90-91) carried correctly.

### 4. Figures — every graph description traces to source solution prose, except one coordinate (below). The 76.2a coordinates `(−2,−1)` filled / `(4,2)` hollow are *derivable*, not invented: a decreasing segment would force `−1 < f(x) ≤ 2`, contradicting source line 73.

### 5. Errors block — all six `wrong` lines genuinely wrong, all six `right` lines genuinely right. Verified individually.

### 6/7. No condescension; the hard step (`a²b = a × ab`) is stated explicitly three times rather than waved at. The five-minute script is sayable and covers every judgement call in the lesson.

---

## Findings

**HIGH — `tutor/management/commands/seed_saxon_76.py:262-263`** — the summary table's "how you write it" column over-generalizes, and Example 76.1b in this same lesson is the counterexample.
```python
{"cells": ["the graph touches the edge of the grid",
           "it keeps going that way forever", "all R (no endpoint at all)"]},
```
The table's own caption is per-END (`"What each kind of end means"`, line 255), so row 3 describes *one* end — but the answer column jumps to `all R`, which is only correct when *both* sides run off. Source line 45: the square-root curve "continues forever in both the +x and +y direction" yet `domain = range = R≥0`, not `all R`. A student applying this cheat-sheet row literally gets 76.1b wrong. The third cell should read something like "no endpoint on that side" (with `all R` reserved for both-ends). Related, milder: the errors item at line 368-369 (`wrong: domain: −6 ≤ x ≤ 6` / `right: domain = all R`) names no graph, so it silently inherits the same both-ends assumption.

**MEDIUM — `seed_saxon_76.py:204-205`** — an invented coordinate the author could not see.
```python
"question": "A V-shaped graph. Its bottom point sits at (0, 0). ..."
```
The source gives only the *height* of the bottom, never its x-position — line 84-86: `"the graph starts at f(x)=0 and ends at f(x)=4 on the right and f(x)=5 on the left"`, and line 90-91: `"we will include the bottom, or vertex of the graph in the range"`. Nothing fixes the vertex at x = 0. It does not change either answer, but it is a fabricated figure detail — and it is mildly implausible, since a vertex at the origin with ends at (−4,5) and (4,4) is not any parent shape she knows. `"Its bottom point sits at f(x) = 0"` would be both true and sufficient.

**LOW — `seed_saxon_76.py:212-217`** — drops Saxon's stated heuristic for 76.2b's range. Source line 85-86: `"Pick the larger of the two positive endpoints, f(x)=5."` The seed instead reasons "The highest output is 5, up at the hollow end". Same answer, better general principle — but that exact sentence is what her DIVE worked solution shows.

**LOW — `seed_saxon_76.py:315`** — collapses Saxon's displayed intermediate line. Source 110-111 shows `9a + 4a = 13a`; the seed goes straight from `3a + 6a + 4a` to `13a`.

**LOW — `seed_saxon_76.py:185`** — `"The leftmost point sits above x = −2"` for a point whose f(x) is −1, i.e. below the axis. "Sits at x = −2" avoids the collision.

**LOW — `seed_saxon_76.py:30, 238`** — `1/x` is in the reference gallery, but source line 16-17 scopes 76A: `"unlike Lesson 66A, which focused on discontinuous functions, our focus here is on continuous functions."` The stated domain/range for it is correct; it is a scope drift, not an error. (`a^x` is correctly included — it is Practice Set 76.2.)

**LOW — `seed_saxon_76.py:267-268`** — `"a **house rule** for this course, not a law of mathematics"`. Including the vertex is simply correct (the vertex is a point on the graph); Saxon's own hedge at line 90 is what is being mirrored, so this is defensible, but the phrasing could leave her thinking real mathematics disagrees.

**VERDICT: NEEDS WORK** — arithmetic, method and notation are faithful throughout; two lines (the table's `all R` cell at 262-263 and the invented vertex coordinate at 205) need correcting before she uses this.
##### LESSON 77 #####
## Verification of arithmetic (all recomputed by hand)

| Authored claim | Location | Recomputed | Source |
|---|---|---|---|
| `0.1065 × 700 = 74.55` | seed_saxon_77.py:171 | 74.55 ✓ | lesson_077.txt:63 |
| `74.55 − 21.122 = 53.428` | :173, :175 | 53.428 ✓ | :63 `f(700) = 74.55 -21.122 = 53.428 mm` |
| `b = 2` from (0,2) | :189 | ✓ | :83 "The coordinate (0,2) gives away the y-intercept, b=2" |
| `Δy = 3.5 − 2 = 1.5`, `Δx = 3 − 0 = 3`, `m = 0.5` | :193, :196, :200 | ✓ | :85 "∆y=3.5-2 = 1.5, and ∆x=3-0=3 … 1.5/3 = 0.5" |
| `y = 0.5x + 2` | :203 | ✓ | :88 |
| `0.5 × 8 + 2 = 6` (check on unused row) | :207 | 6 ✓ matches table row (8,6) at :77 | derived, valid |
| `f(7) = 3.5 + 2 = 5.5` | :210 | ✓ | :90-91 |
| Table Δ column: 0.5/0.5/0.5/0.5 | :277-281 | (1→1.5)/1=0.5; (1.5→2)/1=0.5; (2→3.5)/3=0.5; (3.5→6)/5=0.5 ✓ | all five points from :73-77 |
| `m = 3 / 1.5 = 2` (wrong line) | :241 | = 2 ✓, genuinely the flipped fraction | — |
| `0.1065 × (700 − 21.122) = 72.301` (wrong line) | :253 | 678.878 × 0.1065 = 72.300507 → **72.301** ✓ | — |
| "off by nearly 19 mm" | :255 | 72.301 − 53.428 = 18.873 ✓ | — |
| `y = 2x + 2` "misses every point except (0,2)" | :378-379 | x=−2→−2≠1; −1→0≠1.5; 0→2 ✓; 3→8≠3.5; 8→18≠6 ✓ exactly one hit | — |
| `0.1065 × 850 = 90.525`; `− 21.122 = 69.403` | :298-300 | ✓ | :98-100 (Practice Set 77 #1) |
| `m = 0.1065 mm per gram`, `b = −21.122` nonsense at zero | :417-420 | ✓ correct unit reading; x=mass g, y=stretch mm confirmed by :64 | :64 |

**No invented numbers, no arithmetic error anywhere.** Errors-block "wrong" lines are all genuinely wrong and "right" lines all genuinely right (check 5 passes). No figure is described that isn't on the page — the stepper prints the five points inline (:180) and the parent note at :431-433 explicitly discloses the missing scatter graph (check 4 passes). Nothing condescending, and the hard step (slope) is done in full, digit by digit, not hand-waved (check 6 passes). The parent script (:352-373) is sayable and does teach b-then-m-then-substitute (check 7 passes, with one caveat below).

---

## Findings

**HIGH — the lesson deletes Saxon's first instruction for Ex. 77.2: graph the points.**
Source, lesson_077.txt:70 — `Example 77.2 Graph the data shown, and create a linear equation that fits the data.` and :78-80 — `In Lessons 68 and 70, you were given linear equations and asked to graph them by plotting data points. Here, you first need to plot the data points, then create an equation based off the pattern.` Saxon then uses the graph as a *second* route to slope, :86 — `Alternatively, observe the graph and notice the rise/run = 1/2 = 0.5.`
Authored, seed_saxon_77.py:178-212 (the whole KIND_STEPPER) and the KIND_STEPS recipe at :113-134: four moves — read b, pick two points, write it, check it. **Plotting appears nowhere.** :183-185 even opens with `"Look first" … "Five points and no equation anywhere"` — a table stare, not a graph.
This matters concretely, not abstractly: her DIVE practice set problem 2 is lesson_077.txt:101 — `277. Graph the data shown, and create a linear equation that fits the data. Then find f(5).` She will be asked to graph, will not have been shown it here, and will also not have the rise/run-off-the-graph route Saxon gives her as the alternative.

**MEDIUM — "first time" contradicts the source's own sentence.**
Source :19-21 — `You already partially created a linear equation from data in problems like Ex. 74.5. In those problems, you observed a linear trend and then estimated the slope.`
Authored :27-28 — `"Every graphing lesson so far handed you the equation and asked for points."`; :323-324 — `"Everything you've graphed until now started with an equation and ended with points"`; :330-331 — `this lesson is her first time **finding them instead of being given them**`; docstring :6-7 — `This is the first lesson where she builds the rule`. Lesson 74 was. The lesson's own "Where this sits" (:428-429) gets it right — `74 (spotting a linear trend in data and estimating its slope)` — so the page argues with itself. If she says "we did this in 74," she's right and the page says she isn't.

**MEDIUM — "Both tables in this lesson" — there is one table, and the other example has no table at all.**
Authored :117-118 — `"Find the row where **x is 0** and take its y. Both tables in this lesson hand it to you."` The lesson contains exactly one table (KIND_TABLE, :273-286, Ex. 77.2's points). Ex. 77.1 is given as an equation, has no table, and its `b = −21.122` cannot be read off one — there is no x = 0 row anywhere for the spring. Same mismatch in the masthead, which displays the *spring* formula at :30 and immediately captions b as :33-34 — `"Read it straight off the table; there is nothing to calculate."` For the equation shown directly above that sentence, that is false.

**MEDIUM — the REVEAL is Practice Set 77 problem 1, answer printed.**
Source :98-100 — `177. (C) For the spring-mass data … estimate the length the spring is stretched when a mass of 850 g is hung from it. Round to 3 d.p.`
Authored :296-300 — `"Same spring, same equation, but an 850 g mass … **69.403 mm.**"` The arithmetic is right and it is framed as a self-check, but it is her assigned problem 1 with the worked answer on the teaching page. Either change the mass or accept that problem 1 is now free.

**LOW — the Δ table lists across before up, against its own mnemonic.**
Authored :275 — `"headers": ["x", "y", "across (Δx)", "up (Δy)", "Δy / Δx"]`, while the #1 error at :243 is `Slope is **rise over run** — the up part goes on top` and the script drills `"up, over, across"` (:380). The single most dangerous mistake on the page is reading the fraction backwards, and the table's column order rehearses it backwards.

**LOW — Saxon's word "trendline" never reaches her.**
Source :71 — `This is an exact equation, not a trendline as in Ex. 77.1.` and :102-103 repeats it in practice problem 2 — `You are not making a trendline that simply follows the pattern`. The lesson teaches the distinction well (:263-269, :75-77) but only ever calls it "trend"/"real data". She meets the actual noun cold, on the practice set.

**LOW — "The spring at the top of this lesson" (:52-53) and "200 grams. 400 grams. 600 grams." (:44-45).** The former resolves only to the masthead `formula` string (:30), which is a fair reading but phrased as though pointing at a picture. The latter are x-axis tick labels in the source (:37), not measurements the source states were taken — harmless scene-setting, but not "from the source" in the strict sense.

## Test run (verbatim)

```
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
....................
----------------------------------------------------------------------
Ran 20 tests in 0.660s

OK
Destroying test database for alias 'default'...
Found 20 test(s).
System check identified no issues (0 silenced).
```

Note: the arithmetic suites pass, but they clearly do not encode a "does the lesson teach Saxon's plotting step" check — the HIGH finding above is invisible to them.

**Verdict: NEEDS WORK** — the mathematics is flawless, but Ex. 77.2 is taught table-only when Saxon teaches plot-then-derive, and her practice set asks her to graph.
##### LESSON 78 #####
## Verification of the mathematics

**Every worked example recomputed against the source, line by line.**

| Authored | Source | Verdict |
|---|---|---|
| `(2⁰x⁻²y⁴/z)¹² = (x⁻²y⁴/z)¹² = x⁻²⁴y⁴⁸/z¹² = x⁻²⁴y⁴⁸z⁻¹²` (seed:137) | `x−2y4/z(…)12 = x−24y48/z12 = x−24y48z−12` (source:39‑48) | identical chain, identical intermediate steps. −2×12=−24 ✓, 4×12=48 ✓, 1×12=12 ✓ |
| `(3xy⁻²/t⁴)⁻³ = 3⁻³x⁻³y⁶/t⁻¹² = t¹²x⁻³y⁶/3³ = t¹²x⁻³y⁶/27` (seed:148) | `= 3−3 x−3y6/t−12 → t12 x−3y6/33 = t12 x−3y6/27` (source:58‑62) | identical, including Saxon's own three-stage chain. 1×(−3)=−3 ✓, (−2)(−3)=+6 ✓, 4×(−3)=−12 ✓, 3³=27 ✓ |
| `(3√x)² = (3x^(1/2))² = 3²x¹ = 9x` (seed:166) | `32x1 = 9x` (source:81) | ✓ |
| `(3x^(1/3))² = 3²x^(2/3) = 9x^(2/3)` (seed:174) | `2(1/3)=2/3, so just leave the simplified exponent as 2/3` (source:83) | exponent ✓; coefficient inferred — see MEDIUM‑4 |
| `t = 400/60 = 40/6` → `6.666…` → `6.7 hours` (seed:250‑256) | `t=400/60=40/6 = 6.667 = 6.7 hours` (source:115) | ✓ 400/60 = 6.6̄, 1 d.p. = 6.7 |
| `19.3/1 = M₂/50 → M₂ × 1 = 19.3 × 50` → `965 g` (seed:281‑287) | `M2(1) = 19.3(50)`, `M2 = 965 g` (source:132‑133) | ✓ 19.3×50 = 965 |
| Reveal: `8.96 × V₂ = 75`, `V₂ = 75 ÷ 8.96 = 8.370… → 8.4 mL` (seed:323‑325) | practice 578 (source:153‑155); method from source:137‑139 | ✓ 75/8.96 = 8.37053…; 8.96×8.4 = 75.26 |
| `(a xᵐ yⁿ / zᵖ)ᵏ = aᵏ xᵐᵏ yⁿᵏ z⁻ᵖᵏ` (seed:311) | generalisation of 78A | algebraically correct ✓ |

**Errors block, each pair checked independently** (seed:332‑383): `2⁰=1` ✓; `−2+12=10` is the genuine add-instead-of-multiply artefact and `x⁻²⁴` is right ✓; `2⁻³ = 1/8` ✓ (not −8); `3³ = 27` ✓; `400×60 = 24,000` ✓ as the stated wrong answer, `6.7` right ✓; `19.3/50 = 0.386` ✓ as the wrong answer, `965` right ✓. The claim **"off by a factor of 81"** (seed:346‑347, repeated at seed:473) is exact: `3 ÷ (1/27) = 81` ✓.

**Method fidelity:** Saxon's order is preserved everywhere — 78.3 rearranges then evaluates, 78.4 substitutes then cross-multiplies, and the lesson names that contrast explicitly (seed:277‑279, table seed:292‑308), matching source:133‑137. Cross-multiplication is attributed to Lesson 53 (source:128) ✓, √ = ½ power to Lesson 30 (source:73) ✓, Saxon's three-line definition of *simplify* is quoted essentially verbatim (seed:84‑97 vs source:17‑19) ✓, and rule 3 is correctly used to justify why finished answers keep negative exponents. **No figure is described that the author could not see** — the lesson never references a graph, diagram or "the figure above".

---

## Findings

**HIGH — seed_saxon_78.py:326‑329 — the reveal's sanity check states a false quantity, and states it as confirmation.**
> `"Sanity check: copper is nearly nine times as dense as water, so 75 g of it should be a small lump — about a tablespoon and a half. 8.4 mL is exactly that."`

A tablespoon is ~15 mL, so "a tablespoon and a half" is ~22.5 mL. 8.4 mL is a bit over **half** a tablespoon (~1.7 teaspoons) — off by a factor of 2.7. The rest of the sentence is right (8.96 ≈ 9× water ✓), which makes it worse: the wrong clause is the one carrying the words "is exactly that." This is the page teaching her to check an answer against a physical estimate, and the estimate it models is wrong. Nothing in the source contains it; it is authored flavour. (Compare seed:284‑286, where the same move is done correctly: 965 g ≈ just under a kilogram ✓.)

**MEDIUM — seed_saxon_78.py:366 — an errors-block heading names a legitimate Saxon method as a mistake.**
> `{"name": "Substituting before the letter you want is on its own.", "wrong": "t = 400 × 60 = 24,000 hours", ...}`

Substituting first is not an error — the source says so directly (source:133‑137: *"Sometimes, it makes more sense to rearrange first, and other times evaluating (substituting numbers in) first makes more sense"*), Saxon does it in 78.4, and this same lesson endorses it twice: seed:294 `"Substitute first (78.4)"` and seed:221‑222 `"Neither is more correct."` The actual error the `wrong` line demonstrates is multiplying where you should divide, which is what the `note` correctly explains. The `wrong`/`right` lines are sound; the **name** misdiagnoses them, in the block you have identified as the highest-authority lines on the page. A child who memorises the seven headings memorises one rule that contradicts the table three blocks up.

**MEDIUM — the green test run is near-vacuous for Lesson 78; it is not evidence of fidelity.** `tutor/tests.py:1658` restricts evaluable expressions to `r"[\d\s.+\-*\()]+"` — **`/` is not in the class**, so every division-bearing equation returns `None` and is silently skipped: `t = 400 / 60 = 40 / 6` (seed:250), `M₁ / V₁ = 19.3 / 1` (seed:275), `19.3 / 1 = M₂ / 50` (seed:281) are all unchecked. And `_math_lines` (tests.py:1627‑1637) collects only `data["math"]`, `steps[].math` and `items[].right` — a `KIND_REVEAL` block has neither, so the entire reveal at seed:319‑329 (the 8.4 mL, the division, the tablespoon claim) is invisible to every test. By my trace exactly **one** Lesson 78 equation is actually verified: `M₂ = 19.3 × 50 = 965 g`. The 11 `SyntaxWarning: 'int' object is not callable` lines in the run are the same failure mode elsewhere — malformed expressions eval'd, `TypeError` swallowed at tests.py:1662, line silently unchecked.

**MEDIUM — seed_saxon_78.py:155, 174, 176 — the coefficient in Example 78.2b is inferred, not sourced.** Source:70‑71 carry the problems as images (`a)` / `b)` extract to nothing) and source:84‑85 (b's solution line) is blank. The only surviving evidence is source:82‑83: *"Simplify like you did in a), except this time the variable has a fractional exponent of 1/3, and 2(1/3)=2/3."* That pins the outer power (2) and the exponent (2/3) but **not the leading 3**. 78.2a's problem is safely recoverable (source:81 `32x1 = 9x` forces `(3√x)²`); 78.2b's `9` is an assumption. If the DIVE image has no coefficient, the lesson tells her `9x^(2/3)` where her answer key says `x^(2/3)` — and she will trust the page over herself. Worth confirming against the printed book before approval.

**LOW — seed_saxon_78.py:319‑329 — the "your turn" is an assigned problem, answered.** It is practice problem 578 verbatim (source:153‑155: copper, 8.96 g/mL, 75 g, round to 1 d.p.). The method exposition is good, but her DIVE practice set now contains one pre-worked item.

**LOW — seed_saxon_78.py:108‑109 — "the whole bag gets used −3 times".** A bag cannot be used −3 times, and the lesson itself insists three times over that a negative exponent is *"a note about which floor, not a negative number"* (seed:190‑191, 357‑358, 396). The one sentence written to build the intuition is the one that undercuts it.

**LOW — Saxon's own scaffolding dropped in two places.** The `t = d/r` flip omits Saxon's Lesson 50 Celsius callback (source:111‑112), and the density block never shows Saxon's literal general form `M1V2 = M2V1` for the solve-for-V₂ case (source:137‑139) even though the reveal is exactly that case. Neither is an error; both are recall hooks the source deliberately planted.

**LOW — seed_saxon_78.py:511‑516, parent "Extend it".** `(2x³/y)⁰ = 1` is given without the nonzero caveat the lesson is otherwise scrupulous about (seed:116, 338). The gold-ring extension (`0.5 mL` displaced) gives the parent no answer to check against — it is 19.3 × 0.5 = **9.65 g**.

**Checked and clean:** no condescension (the "children resist because it looks babyish" line is parent-facing and is followed by a real reason, seed:499‑500); the hard step is not hand-waved — the coefficient inside the bracket, the sign flip, and the 3⁻³→1/27 move each get their own labelled step and their own error entry. The five-minute script (seed:443‑466) is sayable as written and teaches Saxon's method, not a substitute: step 1 `(3x)² → 3²x² → 9x²` ✓, step 2 derives −24 by twelve copies of `1/x²` ✓ (that is a genuinely good move — it makes the rule hers), step 3 `2⁰ = 1` ✓, step 4 hands her `t¹²x⁻³y⁶/3³` and asks "is this finished?" ✓ (rule 2, the actual mark-loser), step 5 `40 × 3 = 120` ✓ then flips to the blank.

---

## Test run (verbatim, last 20 lines)

```
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
<string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
....................
----------------------------------------------------------------------
Ran 20 tests in 0.600s
OK
Destroying test database for alias 'default'...
Found 20 test(s).
System check identified no issues (0 silenced).
```

Files: `C:/Users/lopez/code/django-projects/homeschool-hub/tutor/management/commands/seed_saxon_78.py`, `C:/Users/lopez/code/django-projects/homeschool-hub/saxon_source/lesson_078.txt`, `C:/Users/lopez/code/django-projects/homeschool-hub/tutor/tests.py`

**VERDICT: NEEDS WORK** — the taught mathematics is faithful to Saxon in every worked example, method and notation, but one sanity check states a false quantity as confirmation (seed:328) and one errors-block heading calls a Saxon-endorsed method a mistake (seed:366); both live in the lines she is most likely to trust.
##### LESSON 79 #####
## Fidelity review — Saxon Pre‑Algebra Lesson 79

**Test run (verbatim tail):**
```
....................
----------------------------------------------------------------------
Ran 20 tests in 0.658s

OK
Destroying test database for alias 'default'...
Found 20 test(s).
System check identified no issues (0 silenced).
```

### What is clean (verified by hand)

- **Ex. 79.1a** — source `lesson_079.txt:27-32` (`b = -1` … `rise up 1, then right 2` … `at (2,0)` … `m = rise/run = 1/2 = 0.5` … `y=0.5x-1`) is reproduced number-for-number at `seed_saxon_79.py:162-190`. Check step recomputed: `0.5(4) - 1 = 1`, so `(4,1)` is genuinely on the line.
- **Ex. 79.1b** — source `:38-43` (`b = 2` … `"rise down" 2, then right 1` … `at (1,0)` … `m = -2/1 = -2` … `y=-2x+2`) matches `:196-219` exactly.
- **Practice 6** (source problem `677.`, `:61-68`) — all five pairs satisfy `y = x + 1` (`-2+1=-1`, `-1+1=0`, `0+1=1`, `2+1=3`, `5+1=6`); `m = 2/2 = 1`; `f(3)=4`. Correct, and it correctly flags it as exact rather than a trendline.
- **The practice line is real.** All seven `PRACTICE_LINE` points (`:25`) satisfy `y = -0.5x + 1`, all sit inside the `-6..6` window, all are lattice points, and `axisTicks` in `static/js/portal-grid.js:232` gives step 1 across a span of 12 — so every coordinate she needs is labelled. The REVEAL (`:290-297`) recomputes correctly.
- **No invented figures.** Source practice problems `179.`/`279.` are graphs-only; the author correctly declined to reconstruct them and built its own line instead (docstring `:11-13`).
- **Errors items 1, 2, 3, 5 are all genuinely wrong-over-right.** Item 3's "wrong" line is verifiable: `y = 0.5x - 1` really does cross the x-axis at `2`, so `:316` is a true statement of a false inference. Item 5's swap is arithmetically the real swap: `y = bx + m` with `b=-1, m=0.5` is `y = -x + 0.5` (`:329`).
- Tone: no condescension found; the hard step (landing on a lattice point and signing the rise) is stated explicitly, not waved past.
- Widget claims check out against `static/js/portal-grid.js`: `cfg.points` pre-draws (`:343`), the button label is literally `"✏️ Pen"` (`:437`).

---

### HIGH

**1. `seed_saxon_79.py:119-122`, `:324-325`, `:378-380` — Saxon's "integer" is rewritten as "whole number", which makes the rule false and contradicts this lesson's own worked example.**

Source `lesson_079.txt:15-17`:
> "ALL problems related to Lesson 79 have slopes that are **integers** or simple fractions, and y-intercepts that are **integers**."

Authored `:119-121`:
> "in **every** Lesson 79 problem the slope is a **whole number** or a simple fraction, and the intercept is a **whole number**."

Repeated at `:324-325` ("every slope in this lesson is a whole number or a simple fraction") and `:378-380` ("Every slope in this lesson is a whole number or a simple fraction, and every intercept is a whole number").

Saxon defines whole numbers as `{0, 1, 2, …}` and integers as including negatives — that distinction is Saxon's own vocabulary and it is load-bearing here. Two consequences:
- The lesson's own Example 79.1b answer is `m = -2` (`:213`, `:217`) and Example 79.1a's intercept is `b = -1` (`:176`). Neither is a whole number. The page states a rule its own worked examples violate.
- She is told to use this as a *self-check* ("`m = 0.37` is not an unusual answer. It is a wrong one", `:121-122`). Applied as written, it tells her to reject her own correct `m = -2` or `b = -1` on the DIVE practice set. That is the exact failure mode the review is meant to prevent.

Notably the parent guide gets it right — `:410-411`: "every slope in Lesson 79 is an integer or a simple fraction, and every y-intercept is an integer" — as does the docstring `:13`. Only the three student-facing statements are wrong, which confirms it is a slip, not a deliberate simplification.

---

### MEDIUM

**2. `:180`, `:185`, `:213` — the two-point subtraction formula is used in the display math; Saxon uses neither the formula nor subtraction here.**

Source `:31`: `m = rise/run = 1/2 = 0.5`. Source `:42`: `m = rise/run = -2/1 = -2`.
Authored `:180`: `m = (0 - (-1)) / (2 - 0) = 1/2 = 0.5`; `:213`: `m = (0 - 2) / (1 - 0) = -2/1 = -2`.

The arithmetic is right and the surrounding prose does teach counting ("Rise 1, run 2", `:179`). But the *displayed* line — the one she copies — is `(y₂-y₁)/(x₂-x₁)`, machinery this lesson does not introduce and which requires her to subtract a negative in the very first example. Saxon deliberately keeps it to counting squares.

**3. `:108-112`, `:136`, `:428-429` — run-first instruction contradicts the rise-first order used by the lesson's own worked examples and by Saxon.**

Source `:28`: "From b, **rise up 1, then right 2**." Source `:39`: "From b, 'rise down' 2, **then right 1**."
Authored Idea 3 `:108-111`: "walk **right** until your finger lands exactly on a corner… How far up or down did you have to go?" Recipe step 3 `:136`: "From that point, walk right to the next corner." Parent script step 4 `:428-429`: "Walk right until you land exactly on a corner. How far right did you go, and did you go up or down?"

But the stepper `:178` says "Go **up 1**, then **right 2**" and the worked example `:211` says "go **down 2**, then **right 1**" — Saxon's order. She is shown two different walking procedures in one lesson, and the parent is scripted on the non-Saxon one.

**4. `:322` — the "wrong" line in error pattern 4 is not arithmetically what the stated points give, and the point is nowhere near the line.**

> `"wrong": "from (0, 2) towards somewhere near (0.7, -0.4)  →  m = -3.4"`

`(-0.4 - 2) / (0.7 - 0) = -2.4/0.7 = -3.4285…`, not `-3.4`. More seriously, the line in question is `y = -2x + 2` (its "right" line, `:323`), and at `x = 0.7` that line is at `y = 0.6`. The point `(0.7, -0.4)` is a full unit off the line — so it does not illustrate "a point the line only **passes near**" (`:321`) at all. The errors block is the highest-authority text on the page; its numbers should survive being checked.

**5. `:227-228` — a false universal about `y = mx + b`, contradicted by the lesson's own parent guide.**

> `{"symbol": "y = mx + b", "plain": "the standard form every straight line can be written in"`

versus `:489-491`: "That line has no slope at all and **cannot be written as** `y = mx + b`." (Using Saxon's word "standard form" is correct fidelity; the word "every" is what is wrong.)

**6. `:273-274` — the tool intro promises something that can silently destroy the figure she is asked to read.**

> "You can click anywhere to drop your own dot and count squares with it."

In `static/js/portal-grid.js`, `pointerdown` snaps to the lattice and, if a point is already there, **removes it**: `if (hit >= 0) { points.splice(hit, 1); … readout.textContent = "removed"; return; }`. `Undo` pops the last of the seven seeded points and `Clear` wipes them all, with no restore. A click on any of the seven given dots deletes part of the only line she has — a dead end with no way back.

---

### LOW

**7. `:69` — invented prior-lesson content.** "In Lesson 70 you started with something like `y = 2x + 1`." The source (`:11-12`) names only "Ex. 70.1 and 70.2" with no content. Hedged by "something like", so it is honest, but it is not from the source.

**8. `:164-168`, `:174-175` — "read straight off the picture" when there is no picture.** The stepper's only figure substitute is the coordinate header at `:162`. Lines like "It cuts the up-and-down axis **below** the middle" and "one square **below** the middle" are recoverable from `b = -1`, so it is not unverifiable — but she is repeatedly told to look at something that is not on the page.

**9. `:345-346` — Saxon's vocabulary word dropped.** Source `:62`: "not a **trendline** as in Ex. 77.1." Authored: "not a **line of best fit** like the one in Lesson 77." "Trendline" is the word on her DIVE page.

**10. `:490` — "That line has **no slope at all**."** The standard (and Saxon's) phrasing is *undefined* slope. Minor, and it is in an optional extension.

**11. `:50` — "the paper ran out at 6"** forward-references the tool grid's `-6..6` window, which she has not seen yet at that point in the page.

---

**Verdict: NEEDS WORK** — finding 1 puts a false self-check rule in her hands that would make her reject her own correct answers of `m = -2` and `b = -1`.
##### LESSON 80 #####
## Verification run

```
....................
----------------------------------------------------------------------
Ran 20 tests in 0.709s

OK
Destroying test database for alias 'default'...
Found 20 test(s).
System check identified no issues (0 silenced).
```
(20/20 pass. `saxon_lesson_numbers()` at `tutor/tests.py:1306` auto-discovers seeders, so Lesson 80 *is* covered — I traced `_sides()` over its `math` lines and confirmed `3 − 3 = 0`, `(−4) − (−4) = 0`, `2 − 2 = 0`, `3 − (−5) = 8`, `4 − (−2) = 6`, and the errors block's `right` line `0/6 = 0` are all genuinely evaluated, not compared to literals.)

## Arithmetic recomputation (check 1) — all clean

Every number recomputed by hand:

| authored | check |
|---|---|
| `seed_saxon_80.py:177` `AE: Δy = 3 − 3 = 0` | 0 ✓ |
| `:177` `LJ: Δy = (−4) − (−4) = 0` | 0 ✓ |
| `:181` `BK: Δx = 2 − 2 = 0` | 0 ✓ |
| `:185` `CD: Δx = 3 − (−5) = 8 → Δy = 4 − (−2) = 6` | 8 and 6 ✓ (slope ¾, genuinely oblique) |
| `:101-103` "(−4, 3) and (4, 3) … change in x is 8" | 4−(−4)=8 ✓ |
| `:123-124` "(2, 5) and (2, −3). The change in y is 8" | |5−(−3)|=8 ✓ |
| `:228` `(−2, −3) (−2, 0) (−2, 4) (−2, 5)` all satisfy x=−2 ✓ |
| `:349` table `[[-4,3],[-2,3],[0,3],[3,3],[5,3]]` — every y=3, all inside the ±6 view ✓, and `(0,3)` really is the y-crossing the prose claims at `:353` |
| `:354-355` `(2,−4)(2,−1)(2,0)(2,3)(2,5)` — every x=2, all in view ✓ |
| `:298` `y = 0x + 2` → y = 2, "a horizontal line at height 2" ✓ |
| `:335` `y=3` and `x=3` cross at `(3,3)` ✓ |
| `:467-472` x-axis is `y = 0`, y-axis is `x = 0`, H/V through (3,5) are `y=5`/`x=3`, meeting at (3,5) ✓ |

Source answers are preserved exactly: `lesson_080.txt:54,57` "two lines are horizontal, Lines AE and LJ" / "only line BK is vertical" → `seed_saxon_80.py:187` "AE and LJ are horizontal · BK is vertical". `lesson_080.txt:65-66` "y=4" / "x=1" → `:209` "y = 4 · x = 1". `lesson_080.txt:73-74` "Choice B" → `:235` "Choice B". **No invented answers.**

## Check 5 — errors block: all five verified correct

`:278` `x = 4` for an upright line through 4 on the x-axis ✓ · `:284` `m = 0/6 = 0` for horizontal ✓ · `:290` "vertical: m is undefined" ✓ · `:296` `x = 2` ✓ · `:302` `y = −3` for a flat line through (0,−3) ✓. Every `wrong` line is genuinely false and every `right` line genuinely true. This is the strongest part of the page.

## Check 3 — Saxon vocabulary: largely excellent

`lesson_012.txt:43-45` "horizontal: Flat, in line with the horizon. / vertical: Upright, or straight up and down. Perpendicular to something that is horizontal." → `seed_saxon_80.py:72-75` "**Horizontal** means flat … like the horizon. **Vertical** means upright — straight up and down". The lesson's child-facing pair *flat/upright* is Saxon's own Lesson 12 wording, carried consistently through all 16 blocks. `oblique`, `x-intercept`, `y = b`, `x = c`, `m = Δy/Δx = 0/Δx = 0` all match `lesson_080.txt:11-22` verbatim.

---

# Findings

### HIGH — `seed_saxon_80.py:229-235`: the 80.3 stepper invents the content of choices A, C and D, which the author could not see

Source gives one fact about the distractors — nothing:
> `lesson_080.txt:73-74` — "solution : The equation represents a vertical line with an x-intercept of x=-2, which is Choice B."

Authored:
> `:231-234` — "Rule the others out on purpose: an upright line at +2 is on the wrong side, a flat line through −2 has the letters swapped, and a slanted line is oblique. That leaves **Choice B**."

Nothing in the source says A is x=+2, or that one option is horizontal, or that one is oblique. If her DIVE page shows a different distractor set (e.g. `y = −2`, which is exactly what practice problem 380 at `lesson_080.txt:92` asks about), the elimination she just rehearsed does not match the paper in front of her — and she will trust the lesson over her own eyes.

Same block, check 4: `:217-219` "You are given four graphs … **Do not look at the pictures yet.**" There are no pictures on this page. `KIND_STEPPER` renders title/equation/steps only (`templates/portal/_lesson_blocks.html`), so "the pictures" is a dead reference.

### HIGH — `seed_saxon_80.py:162-188`: 80.1's method is swapped for one that will not work on the matching practice problem, and the swap is nowhere disclosed to the child or the parent

Saxon solves 80.1 **visually**, from a figure, with no coordinates anywhere:
> `lesson_080.txt:41-42` — "Identify which lines in the diagram are a) horizontal and b) vertical. Identify the lines by using only the two outside points."
> `lesson_080.txt:53-57` — "Horizontal lines are flat. Looking at them on paper or a computer screen, they extend from left to right. Observe that two lines are horizontal… they appear straight up and down. Observe that only line BK is vertical."

Authored 80.1 supplies invented coordinates and teaches subtraction:
> `:164-167` — "A(−4, 3) to E(4, 3) · L(−3, −4) to J(5, −4) · B(2, 5) to K(2, −3) · C(−5, −2) to D(3, 4)"
> `:169-172` — "For each pair, **subtract** to find Δy … and Δx … Whichever one comes out **0** names the line."

Her DIVE practice problem is `lesson_080.txt:77-78`, problem 180: "Identify which lines in the diagram are a) horizontal and b) vertical" — a bare lettered diagram, letters only, **no coordinates to subtract**. The one worked example carrying Saxon's number 80.1 rehearses a procedure she cannot execute on 180. Saxon's actual instruction there is "observe."

The reconstruction is defensible (the figure isn't digitized) and the coordinates are internally consistent — they even keep Saxon's named oblique `LE` oblique, since L(−3,−4)→E(4,3) has Δy=Δx=7. But the honesty lives only in the developer docstring at `:14-18`; **the child's page and the entire `PARENT_CONTENT` say nothing**. The parent guide's "Where this sits" (`:478-483`) never mentions that 80.1 has been restated, so the mediating adult cannot warn her either. Two fixes, either sufficient: (a) keep the visual "observe" language as the primary move and the subtraction as the *check*, or (b) one sentence on the page saying the figure has been replaced by endpoints.

### MEDIUM — `seed_saxon_80.py:157-159`: the sentence she is told to memorise "word for word" is not the source's words, and the half that was cut is the half that tells her which axis

Source:
> `lesson_080.txt:27-28` — "Equations for horizontal and vertical lines equal the value where they cross the **x (vertical) or y (horizontal)** axis."

Authored:
> `:157-159` — "Saxon says it in one sentence, and it is **worth memorising word for word**: *equations for horizontal and vertical lines equal the value where they cross the axis.*"

The dropped parenthetical *is* the mapping (vertical line → x-axis, horizontal line → y-axis). What's left — "the axis" — is precisely the ambiguity that the lesson itself names as the #1 error at `:300-305` ("Reading the number off the wrong axis"). Same truncation is repeated at `:367-369` (recap) and `:397-399` (parent guide). Restore the parenthetical, or drop the "word for word" claim.

### MEDIUM — `seed_saxon_80.py:102-103`, `:115-116`, `:414-415`: "zero divided by *anything* is zero" contradicts the lesson's own rule at 0/0

> `:102-103` — "Zero divided by eight is zero — and zero divided by *anything* is zero."
> `:115-116` — "The bottom number never mattered — **zero over anything is zero.**"
> `:414-415` (parent script) — "*'And zero divided by anything else?'* Still zero."

Ten lines later the lesson is emphatic that division by zero is undefined (`:126-128`). A 12-year-old who is being taught to reason — and this lesson explicitly wants that (`:475-476`) — will ask about 0 ÷ 0, and both of the lesson's absolute rules answer it, differently. Source says only `0/∆x = 0` (`lesson_080.txt:12`), where Δx is never 0 for two distinct points. "zero over any *other* number" costs one word and is true.

### MEDIUM — `seed_saxon_80.py:473-476`: the parent guide arms her to contradict Saxon's own wording without flagging it

> `:474-475` — "**'Is `x = 2` even a function?'** It is not — one x with endlessly many y values."

Mathematically correct. But Saxon's Lesson 80 is titled "More on Linear **Functions**: Horizontal and Vertical Lines" (`lesson_080.txt:6`) and its own definition reads "x-intercept: The location where a **function** crosses the x-axis. For vertical lines, they are defined by their x-intercept" (`lesson_080.txt:20-21`) — i.e. Saxon is calling vertical lines functions. Since this is offered as a thing "satisfying for a 12-year-old to be able to argue," she may well argue it at her book and be told she's wrong. One clause ("Saxon's lesson title calls these all 'linear functions' — that's the loose usage; strictly…") disarms it.

### LOW — `seed_saxon_80.py:256-258`: definition paraphrase drops Saxon's word

Source `lesson_080.txt:20`: "The location where a **function** crosses the x-axis." Authored: "where a **line** crosses the x-axis." Harmless in isolation, but it is the same word whose loss creates the MEDIUM above.

### LOW — `seed_saxon_80.py:268-270`: hedged where Saxon is flat

Source `lesson_080.txt:21`: "since they **don't have** a y-intercept." Authored: "it **may** never cross the y-axis at all." The hedge is technically the more careful statement (x = 0 *is* the y-axis, a case the lesson itself raises at `:467-468`), but it reads as uncertainty about a rule Saxon states without one.

### LOW — `seed_saxon_80.py:171-172` vs `lesson_080.txt:51-52`: the "either order" example was renamed

Source illustrates with "oblique line **LE** can also be written **EL**"; authored uses "**AE** and **EA**". Fine, but LE was available and is the line Saxon actually names as oblique — the authored example instead promotes **CD**, a line Saxon's solution never mentions.

### LOW — `seed_saxon_80.py:123-124` vs `:245`: sign convention not followed in prose

`:245` defines "Δy = second y − first y". For "(2, 5) and (2, −3)" that is −8; the text says "The change in y is **8**". Magnitude-only, and immaterial here (it exists only to show Δx = 0), but the worked example at `:185` does follow the signed convention, so the two blocks model different habits.

### LOW — `seed_saxon_80.py:351-353`: the tool gives away its own answer in the same paragraph that sets the task

`:341-342` asks her to "look for what all five have in common"; `:351-353` — the very next visible text — lists the points *and* answers it ("the equation is **y = 3**"). The second table at `:354-356` is sequenced correctly (points, then "Say its slope out loud" with no answer given). Consider hiding the first answer the same way.

### LOW (informational) — `seed_saxon_80.py:349`: `config["table"]` is inert

`portal-grid.js` never reads `cfg.table` (only `cfg.points`, line 343); the template just hands `config` to `json_script`. So the table exists only for `_unplottable()` validation and for the prose at `:351`. Nothing breaks — the points *are* listed in `after` — but "Plot the five points listed underneath" (`:341`) is satisfied by prose, not by a rendered table, and a future editor changing `:349` alone would silently change nothing. (Verified the "Clear" button referenced at `:354` does exist: `portal-grid.js:451`.)

## Checks 6 and 7 — clean

No condescension found. The hard step is not hand-waved: `:126-128` explicitly refuses the two comfortable lies ("Not \"it equals zero,\" not \"it equals infinity\" — there is no answer at all"), and `:130` names the real reason the formula is abandoned ("The formula is not hard here — it is *unusable*"), which is exactly Saxon's `lesson_080.txt:16-17` "Since the standard linear equation is therefore undefined, we don't use it for vertical lines."

The five-minute script (`:410-427`) is sayable verbatim — I read it aloud against the clock; it runs about four minutes with pauses. It teaches Saxon's derivation in Saxon's order: Δy = 0 → m = 0 (step 1-2, matching `lesson_080.txt:11-12`), the `mx` term collapsing to `y = b` (step 3, matching `lesson_080.txt:12-13`), Δx = 0 → undefined → `x = c` (step 4, matching `lesson_080.txt:15-18`), then the read-one-number move (step 5). Step 5's numbers, 4 and 1, are Saxon's own from Example 80.2. Every step ends in a question with a waitable answer.

---

**VERDICT: NEEDS WORK** — the mathematics is sound and the errors block is trustworthy, but 80.3 fabricates distractors the source never describes, and 80.1 silently substitutes a method that will not work on the practice problem it is preparing her for.