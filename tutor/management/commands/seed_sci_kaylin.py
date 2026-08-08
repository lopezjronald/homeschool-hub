"""Seed Kaylin's Grade 7 Integrated Science "mission" course into the app.

Same in-app, no-AI, no-new-UI pattern (see _mission_seed). Grade 7 additions folded
into the blocks: a Claim–Evidence–Reasoning (CER) completion line, PhET "Digital Lab"
links, the standing safety rule on every card, ⚠️ ADULT ASSIST banners (stove / hot
water: Missions 3, 9, 15), a ⏰ freeze-the-night-before flag (Mission 2), and 🔁
multi-day/multi-week reminders. Completion = a LessonProgress 'done' mark. Mission
text is VERBATIM from the family's commissioned research build.

    python manage.py seed_sci_kaylin            # defaults to child "Kaylin"
"""
from django.core.management.base import BaseCommand

from curricula.blueprints import SCIENCE_G7
from tutor.models import LessonBlock

from ._mission_seed import add_journal, resolve_child, setup_course, upsert_mission

SAFETY = ("🛟 **Safety:** Anything with the stove, boiling water, or open flame needs "
          "Dad (those missions are flagged ⚠️). Everything else is solo. Vinegar + "
          "baking soda is always safe — but **never mix cleaning chemicals**.")

# The RECAP now sends her to the lab notebook (a real place to record the CER),
# instead of just telling her to "write" it with nowhere to put it.
COMPLETION_ITEMS = [
    "Open your **Lab Notebook** below 👇 and write your **CER line** + **3 facts**.",
    "**Turn it in** so Dad can review your reasoning and stamp the mission complete.",
    "**Snap a photo** of the experiment (or a PhET screenshot) for your Work Log.",
]

JOURNAL_INTRO = (
    "Think like a scientist. 🔬 Record your Claim–Evidence–Reasoning and the facts you "
    "found, then press **Turn in** — Dad will review your reasoning and stamp the mission. "
    "Add your experiment/PhET photo to your Work Log too."
)


def journal_questions(m):
    """Kaylin's lab-notebook reflection: the CER line + 3 facts."""
    return [
        ("application",
         "**Claim – Evidence – Reasoning.** Finish the frame in full sentences: "
         "*I claim ___ because I observed ___, which happens because ___.*",
         "Claim = what you found. Evidence = what you measured/saw. Reasoning = the "
         "science (particles, forces, energy…) that explains why."),
        ("application",
         "**3 facts I learned** in this mission.",
         "One clear sentence each."),
    ]

# n, title, time, hook (Hook/PhET/resource — markdown), steps (VERBATIM), check;
# optional adult / prep / note.
MISSIONS = [
    # ---- Unit 1 — Matter & the Particle Model (MS-PS1) ----
    {"n": 1, "title": "Everything Is Particles", "time": "40 min",
     "hook": "**PhET Digital Lab** → [States of Matter: Basics](https://phet.colorado.edu/en/simulations/states-of-matter-basics) → run it: heat and cool the atoms, switch solid/liquid/gas. Play 10 minutes. ☐ Sim completed (screenshot taken).",
     "steps": [
        "Learn: All matter is made of particles (atoms/molecules) in constant motion. **Solid** = locked in place, vibrating. **Liquid** = touching but sliding. **Gas** = flying free. Temperature = how fast they're moving.",
        "Real-world proof: drop ONE drop of food coloring into (a) a glass of ice-cold water and (b) a glass of hot tap water. Don't stir. Time how long each takes to fully spread.",
        "Explain the race using particle speed.",
     ],
     "check": "Two timed measurements + CER line."},
    {"n": 2, "title": "Ice Balloon Lab", "time": "45 min",
     "hook": "**Exploratorium Science Snack** — [Ice Balloons](https://www.exploratorium.edu/snacks/ice-balloons).",
     "prep": "Fill a balloon with water and freeze it solid the night before.",
     "steps": [
        "(Night before) Fill a balloon with water, freeze solid. Today: peel the balloon off your ice sphere and put it in a big bowl or pot of water.",
        "Investigate for 20 minutes like the Exploratorium scientists: Does it float? (Why — solid water is LESS dense than liquid, super rare!) Sprinkle salt on top and watch channels melt. Add food coloring drops to reveal the melt rivers. Look for trapped bubble patterns.",
        "Write 3 observations and 2 questions your ice ball made you wonder.",
     ],
     "check": "Colored melt-channel photo + CER on why ice floats."},
    {"n": 3, "title": "Phase Change Numbers", "time": "40 min",
     "hook": "Nothing needed — this is a measurement lab.",
     "adult": "Dad runs the stove; you record the temperatures.",
     "steps": [
        "Put ice + a little water in a pot with the thermometer. Record temp every minute as Dad heats it: while ice melts, while water heats, when it boils. Keep a minute-by-minute table (~15 min).",
        "Graph time vs. temperature. Find the two FLAT spots (≈0°C melting, ≈100°C boiling). Weird, right? You kept adding heat but the temp paused.",
        "Learn: during a phase change, energy goes into breaking particle bonds instead of raising temperature. The flats are the fingerprint of phase change.",
     ],
     "check": "Graph shows at least one plateau + explanation."},
    {"n": 4, "title": "Density Tower", "time": "40 min",
     "hook": "Nothing needed — straight to the lab.",
     "steps": [
        "Learn: **Density** = how tightly packed matter is (mass per space). Denser sinks, less dense floats.",
        "Build a density tower in a tall glass, pouring slowly in this order: honey or syrup, dish soap, water (colored), vegetable oil, rubbing alcohol (colored differently, pour over a spoon). 4–5 layers standing on each other!",
        "Drop test: a coin, a grape, a piece of plastic, a bean — predict which layer each stops at, then drop and record.",
     ],
     "check": "Tower photo with 4+ layers + drop predictions vs. results."},

    # ---- Unit 2 — Chemical Reactions (MS-PS1) ----
    {"n": 5, "title": "Signs of a Reaction", "time": "40 min",
     "hook": "Search YouTube **\"evidence of chemical reactions middle school\"** (any short video).",
     "note": "Test (c), the nail rusting in vinegar-water, is a MULTI-DAY check — start it today and look again in 2 days.",
     "steps": [
        "Learn: A **chemical reaction** makes NEW substances. Evidence: gas bubbles, color change, temperature change, light, or a solid (precipitate) appearing. Melting ice is NOT a reaction (same substance) — that's a **physical change**.",
        "Station test — run all four and record evidence: (a) vinegar + baking soda, (b) sugar dissolving in water, (c) a steel-wool or iron nail left in a cup of vinegar-water (start today, check in 2 days — rust!), (d) ice melting.",
        "Verdict table: chemical or physical? Cite the evidence for each.",
     ],
     "check": "Verdict table — (a) and (c) chemical, (b) and (d) physical, with evidence."},
    {"n": 6, "title": "Conservation of Mass — Wait, Weight!", "time": "45 min",
     "hook": "**Exploratorium Snack** — [Wait, Weight, Don't Tell Me!](https://www.exploratorium.edu/snacks/wait-weight-dont-tell-me).",
     "steps": [
        "Put vinegar in a bottle. Put baking soda inside a deflated balloon. Stretch the balloon over the bottle mouth WITHOUT dumping. Weigh the whole rig on the kitchen scale. Record.",
        "Lift the balloon — soda drops in, reaction fires, balloon inflates with CO₂ gas. Weigh again while sealed. Compare!",
        "Learn: mass didn't vanish — atoms just rearranged into new substances (**conservation of mass**). Now unseal and weigh a third time. Where did the missing grams go?",
     ],
     "check": "Three weights recorded; CER explains the sealed vs. unsealed difference."},
    {"n": 7, "title": "Hot and Cold Reactions", "time": "40 min",
     "hook": "Nothing needed — thermometer lab.",
     "steps": [
        "Learn: Reactions that release heat = **exothermic**. Reactions that absorb heat (get cold) = **endothermic**.",
        "Test A: vinegar + baking soda with the thermometer in the cup — record temp before and after (it drops! endothermic).",
        "Test B: steel wool soaked in vinegar 1 min, wrapped around the thermometer inside a jar with the lid on — record temp over 5 minutes (rusting releases heat! exothermic — this is exactly how hand warmers work).",
        "Bonus: dissolve salt in water vs. sugar in water — any temp change?",
     ],
     "check": "Before/after temps for both tests, correctly labeled endo/exo."},
    {"n": 8, "title": "Reaction Engineering — Balloon Blow-Up Contest", "time": "40 min",
     "hook": "**PhET Digital Lab** → [Reactants, Products and Leftovers](https://phet.colorado.edu/en/simulations/reactants-products-and-leftovers) → play the Game mode 10 min. ☐ Sim completed (screenshot taken).",
     "steps": [
        "Learn from the sim: reactions use ingredients in fixed ratios; extra ingredient = **leftovers**.",
        "Contest: fixed vinegar amount (½ cup) in 3 bottles. Vary ONLY baking soda: 1 tsp, 3 tsp, 6 tsp (in balloons, Mission-6 style). Which balloon inflates biggest? Is 6 tsp twice as good as 3?",
        "Find the sweet spot: at some point extra soda does nothing — the vinegar ran out (it's the **limiting ingredient**). Graph soda amount vs. balloon size (rough circumference with string).",
     ],
     "check": "Graph/table of 3 trials + limiting-ingredient explanation."},

    # ---- Unit 3 — Thermal Energy (MS-PS3) ----
    {"n": 9, "title": "Heat Moves Three Ways", "time": "40 min",
     "hook": "Nothing needed.",
     "adult": "Dad handles the mug of hot water.",
     "steps": [
        "Learn: heat flows hot → cold, three ways: **conduction** (touch), **convection** (moving fluids), **radiation** (rays, like the sun).",
        "Conduction race: stand a metal spoon, wooden spoon, and plastic spoon in a mug of hot water with a small dab of butter + a rice grain stuck near the top of each handle. Which butter melts and drops its rice first? Rank the materials as conductors.",
        "Convection viewing: fill a clear bowl with cold water; gently squirt in warm colored water from a bag/cup at the bottom edge. Watch the warm color RISE and circulate — that's convection, the engine of weather and (spoiler) plate tectonics.",
     ],
     "check": "Spoon ranking + convection photo/video."},
    {"n": 10, "title": "Build a Cooler — Design", "time": "45 min",
     "hook": "**Science Buddies** — [Build a Cooler](https://www.sciencebuddies.org/stem-activities/build-a-cooler).",
     "steps": [
        "Challenge: design a container that keeps an ice cube solid the longest. Insulation materials: cardboard, cotton, foil, bubble wrap, towel scraps, foam from the Home Depot run — your pick, your design.",
        "Control first: one ice cube on a plain plate — time how long it takes to fully melt (check every 10 min while doing other things). That's the number to beat.",
        "Build your cooler v1. Sketch the design and label which material blocks which kind of heat flow (foil→radiation, foam/cotton→conduction, sealed box→convection).",
     ],
     "check": "Control time recorded + labeled design sketch."},
    {"n": 11, "title": "Build a Cooler — Test & Iterate", "time": "45 min",
     "hook": "Uses the cooler you built in Mission 10.",
     "note": "Bring your cooler v1 from Mission 10.",
     "steps": [
        "Run identical ice cubes: one in your cooler, one on the plate (fresh control). Record melt times.",
        "Compute your **insulation score**: cooler time ÷ plate time. (2.0 = twice as good as nothing.)",
        "Iterate: change ONE thing in v2 (more layers? air gap? foil facing in?) and re-test. Did the score improve? One change at a time = fair test.",
     ],
     "check": "v1 and v2 scores + which change helped."},
    {"n": 12, "title": "Thermos Autopsy & Home Heat Audit", "time": "35 min",
     "hook": "Nothing needed.",
     "steps": [
        "Apply it: examine a real thermos or insulated cup — identify its tricks (shiny layer, sealed lid, double wall/air gap) and match each to conduction/convection/radiation.",
        "Home heat audit: on a hot Sacramento afternoon, hunt the apartment for heat leaks — sunny windows (radiation), gaps under doors (convection), hot walls (conduction). List the top 3 and propose one cheap fix each (curtains, towel snake, etc.).",
        "Write up the audit like a pro report Dad could actually use.",
     ],
     "check": "Audit lists 3 leaks with mechanism + fix."},

    # ---- Unit 4 — Plate Tectonics & the Rock Cycle (MS-ESS2) ----
    {"n": 13, "title": "The Puzzle Earth", "time": "40 min",
     "hook": "**PhET Digital Lab** → [Plate Tectonics](https://phet.colorado.edu/en/simulations/plate-tectonics) → run it 10 min: stretch and smash plates, watch mountains and trenches form. ☐ Sim completed (screenshot taken).",
     "steps": [
        "Learn: Earth's crust is broken into **plates** floating on hot, slowly-flowing rock. Mission 9's convection currents in the mantle drag them around ~fingernail-growth speed.",
        "Pangaea puzzle: print or trace the continents, cut them out, and fit South America into Africa. Evidence check: matching coastlines + identical fossils on both sides = the continents WERE joined (Pangaea) and drifted apart.",
        "California reality: we live near the **San Andreas fault** where two plates grind past each other — that's why California has earthquakes.",
     ],
     "check": "Assembled Pangaea photo + 2 pieces of evidence stated."},
    {"n": 14, "title": "Boundaries — Where the Action Is", "time": "40 min",
     "hook": "Nothing needed.",
     "steps": [
        "Learn the three boundary types with graham crackers (or cardboard) on a frosting/wet-paper-towel \"mantle\": **divergent** (pull apart → new crust, rift), **convergent** (push together → crumpled mountains — watch the cracker edges buckle!), **transform** (grind past → earthquakes).",
        "Match real places: Mid-Atlantic Ridge→divergent, Himalayas→convergent, San Andreas→transform.",
        "Earthquake demo: press your palms together hard and slide — they stick, stick, then JERK. That jerk is an earthquake releasing stored energy.",
     ],
     "check": "Three boundary demos photographed + real-place matches."},
    {"n": 15, "title": "The Crayon Rock Cycle", "time": "45 min",
     "hook": "**Science Buddies** — [Crayon Rock Cycle](https://www.sciencebuddies.org/stem-activities/crayon-rock-cycle).",
     "adult": "Dad does the hot-water steps (dipping and melting the foil packets).",
     "steps": [
        "Shave 3 old crayons into bits with a scissors edge = **sediments** (weathering!).",
        "Press a foil packet of shavings HARD under books = **sedimentary rock** (layers squeezed together).",
        "Dip the packet briefly in hot water (Dad), then re-press = **metamorphic rock** (heat + pressure, swirled but not melted).",
        "Melt fully in a foil boat floating on hot water, then cool = **igneous rock** (cooled from liquid).",
        "Diagram the full rock cycle with arrows and where heat/pressure/weathering drive each step. Real rocks do this over millions of years; you did it in one afternoon.",
     ],
     "check": "All three \"rocks\" photographed + labeled cycle diagram."},
    {"n": 16, "title": "Rocks of California", "time": "35 min",
     "hook": "**USGS** — [usgs.gov/educational-resources](https://www.usgs.gov/educational-resources) (browse rock ID).",
     "steps": [
        "Field collection: gather 5 different rocks from outside. Test and describe each: color, layers?, crystals/sparkle?, hardness (scratches with a nail or not?).",
        "Best-guess classify each as igneous / sedimentary / metamorphic using your Mission 15 knowledge. (Sierra granite = igneous; Valley sediment = sedimentary — the whole Central Valley floor is river-dumped sediment!)",
        "USGS check: browse rock ID resources to confirm one guess.",
     ],
     "check": "5-rock catalog with observations + classifications."},

    # ---- Unit 5 — Earth's Natural Resources (MS-ESS3) ----
    {"n": 17, "title": "Cookie Mining", "time": "40 min",
     "hook": "**Science Buddies** — [Chocolate Chip Mining](https://www.sciencebuddies.org/teacher-resources/lesson-plans/fossil-fuels-chocolate-chip-mining).",
     "steps": [
        "You're a mining company. Your land = a chocolate chip cookie. Your budget: you \"buy\" tools (toothpick = cheap, paperclip = mid, fork = expensive — set prices). Chips = ore ($ each). Broken cookie land = cleanup fines per crumb zone.",
        "Mine for 5 minutes. Then do the accounting: ore earned − tools − cleanup fines = profit (or loss!).",
        "Learn: resources are unevenly buried, extraction damages land, and cleanup costs are real. Try a second cookie with a different strategy — more careful = more profit?",
     ],
     "check": "Both profit/loss sheets."},
    {"n": 18, "title": "Renewable vs. Nonrenewable", "time": "35 min",
     "hook": "**EIA Energy Kids** — [eia.gov/kids](https://www.eia.gov/kids) (browse energy sources).",
     "steps": [
        "Sort all major energy sources into **renewable** (sun, wind, water, geothermal) vs. **nonrenewable** (coal, oil, natural gas — fossil fuels = ancient buried life, hence \"fossil\").",
        "Bean-jar model: jar of 40 beans = a coal deposit. \"Burn\" 2 the first year, then 4, then 8, then 16 (demand doubles). How many years until empty? Now model solar: a bowl that refills every morning. That's the whole difference.",
        "California audit: look up (search) what powers Sacramento — SMUD's mix includes hydro, solar, wind, and natural gas. List the mix renewable-first.",
     ],
     "check": "Sort correct + bean-jar depletion table."},
    {"n": 19, "title": "Design a Resource Plan", "time": "35 min",
     "hook": "Nothing needed.",
     "steps": [
        "Scenario: you govern an island with coal (cheap, limited, polluting), great sun, strong wind, and one river. Write a 20-year energy plan: what do you build first, what do you phase out, and how do you pay for it (mine some coal early to fund solar?).",
        "Trade-off table: every choice gets a cost, a benefit, and an environmental impact line. No perfect answers — engineering means trade-offs.",
        "Defend your plan to Dad in a 2-minute pitch.",
     ],
     "check": "Plan + trade-off table + pitch delivered."},

    # ---- Unit 6 — Ecosystems & Biodiversity (MS-LS2) ----
    {"n": 20, "title": "Backyard Biodiversity Survey", "time": "45 min (outside)",
     "hook": "Nothing needed — head outside.",
     "steps": [
        "Mark a survey zone outside (park strip, yard, riverbank area) about 10×10 steps. For 20 minutes, count and record EVERY kind of living thing you find: plants (each different kind), insects, birds, spiders, fungi. Tally sheet + photos of mystery species.",
        "Compute your **biodiversity score**: number of different species found. Then survey a \"dead zone\" (parking lot edge) for comparison.",
        "Learn: **biodiversity** = the variety of life. More variety = more stable ecosystem (you'll prove this in Mission 22).",
     ],
     "check": "Two tally sheets with species counts compared."},
    {"n": 21, "title": "Build the Food Web", "time": "40 min",
     "hook": "**California Academy of Sciences** — [How Stable Is Your Food Web?](https://www.calacademy.org/educators/lesson-plans).",
     "steps": [
        "Learn the flow: **producers** (plants — make food from sunlight) → **primary consumers** (herbivores) → **secondary consumers** (predators) → **decomposers** (recycle the dead back to soil). Energy flows one way; matter cycles.",
        "Build a Sacramento Valley web: index cards for sun, oak/grasses, insects, salmon, mice, hawks, coyotes, fungi. Connect with yarn: every \"eats\" relationship gets a string. It's a WEB, not a chain.",
        "Trace one energy path from sun to top predator out loud.",
     ],
     "check": "Physical web photo with 8+ cards and crossing strings."},
    {"n": 22, "title": "Pull a Thread — Ecosystem Jenga", "time": "40 min",
     "hook": "Uses the food web you built in Mission 21.",
     "note": "Bring your Mission 21 food web.",
     "steps": [
        "Experiment on your web: remove ONE species card and every string attached to it. Which other species lost a food source? Mark them. Now remove a second, connected species. Cascade!",
        "Test both versions: remove a highly-connected species (insects) vs. a top predator (hawk). Which removal wrecked more of the web? Count broken strings each time.",
        "CER: claim which species matters most to THIS web's stability, with string-count evidence. Connect to Mission 20: why did the biodiverse zone beat the parking lot?",
     ],
     "check": "Broken-string counts for both removals + CER."},
    {"n": 23, "title": "Competition & Invasion", "time": "35 min",
     "hook": "Nothing needed.",
     "note": "The sprout competition runs over the next week — plant today, observe, and record the result at the capstone.",
     "steps": [
        "Learn: organisms **compete** for limited resources (food, water, space, light). **Invasive species** are outsiders with no local predators that outcompete natives.",
        "Sprout competition test: two cups of soil — plant 3 bean seeds in one, 15 crowded seeds in the other. Same water, same light. Predict which cup grows healthier plants, then observe over the next week (attach results to a later mission's log).",
        "California case: look up ONE real invader (nutria, water hyacinth, or yellow star-thistle) and write 3 sentences on what it outcompetes and why it wins here.",
     ],
     "check": "Both cups planted + invader paragraph."},

    # ---- Unit 7 — Cycling of Matter & Energy (MS-LS1/LS2) ----
    {"n": 24, "title": "Photosynthesis You Can SEE — Floating Leaf Disks", "time": "45 min",
     "hook": "**Science Buddies** — [Photosynthesis Floating Leaves](https://www.sciencebuddies.org/stem-activities/photosynthesis-floating-leaves).",
     "steps": [
        "Punch 10 disks from a fresh spinach leaf with a straw. Suck the air out of them: put disks + baking-soda-water in a syringe (or squeeze bottle), seal, pull vacuum a few times until disks SINK.",
        "Pour into a cup of baking-soda water and set under the brightest light/sun. Time it: as leaves photosynthesize, they produce oxygen bubbles inside and FLOAT one by one. Record how many float every 2 minutes.",
        "Control: identical cup in a dark closet. Compare after 20 min.",
        "Learn: **photosynthesis** = plants use light + CO₂ (from the baking soda) + water to make sugar + oxygen. You just watched the oxygen output in real time.",
     ],
     "check": "Float-count timeline light vs. dark + CER."},
    {"n": 25, "title": "The Carbon & Water Merry-Go-Round", "time": "40 min",
     "hook": "**NOAA Water Cycle Board Game** — [print & play](https://www.nesdis.noaa.gov/about/k-12-education/jpss-education/water-cycle-board-game) or draw your own.",
     "steps": [
        "Water cycle in a bag: draw sun/cloud/sea on a ziplock, add blue water, tape to a sunny window. Over hours: evaporation → condensation drops on the \"sky\" → rain trickles down. Photo-document morning vs. afternoon.",
        "Carbon cycle relay: 6 station cards (atmosphere, plant, animal, soil/decomposers, ocean, fossil fuels). Be a carbon atom: roll a die at each station to see where you travel next (make simple rules). Log your atom's 10-step journey.",
        "Big idea: matter (water, carbon) CYCLES round and round; energy flows THROUGH (sun → out). Nothing is ever \"used up,\" only moved.",
     ],
     "check": "Bag-cycle photos + your atom's journey log."},
    {"n": 26, "title": "Decomposer Detectives", "time": "35 min + weeks of observation",
     "hook": "Nothing needed.",
     "note": "This is a MULTI-WEEK race — set it up now, check it for one minute weekly, and give the final verdict at Mission 30.",
     "steps": [
        "Build a decomposition race: 4 items in labeled ziplock bags with a spoon of damp soil — bread piece, apple slice, foil piece, plastic scrap. Tape to a warm spot. Predict the finish order.",
        "Learn: **decomposers** (bacteria, fungi) break dead matter into nutrients plants reuse — the recycling crew of every food web (your Mission 21 fungi card!). Foil and plastic have no decomposer that eats them — that's the litter problem.",
        "Weekly 1-minute check for the rest of the course; final verdict at Mission 30.",
     ],
     "check": "Bags set up + predictions logged."},

    # ---- Unit 8 — Engineering Design (MS-ETS1) ----
    {"n": 27, "title": "The Egg-Drop Lander — Design", "time": "45 min",
     "hook": "**Science Buddies** — [The Engineering Design Process](https://www.sciencebuddies.org/science-fair-projects/engineering-design-process/engineering-design-compare-scientific-method).",
     "steps": [
        "Mission: land a raw egg from as high as Dad will allow (stairwell? balcony? ladder + driveway?) with ZERO cracks. Materials: anything from the scrap bin — straws, cardboard, balloons, cotton, tape, plastic bags (parachute?), PVC bits.",
        "Follow the real process: DEFINE the problem (impact force kills eggs) → BRAINSTORM 3 different designs on paper (crumple zone? parachute? suspension cage?) → pick one and justify the choice.",
        "Build v1. No testing yet — engineers review before launch.",
     ],
     "check": "3 sketched concepts + built v1 with design rationale."},
    {"n": 28, "title": "The Egg-Drop Lander — Test & Iterate", "time": "45 min",
     "hook": "Uses your egg lander from Mission 27.",
     "note": "Bring your egg lander v1 from Mission 27, plus a few spare eggs.",
     "steps": [
        "Drop test v1 (film it in slow-mo!). Autopsy the result: exactly WHERE did the design fail or succeed?",
        "Iterate: modify ONE subsystem and drop v2. If it survives, RAISE the drop height until failure — engineers find the limit.",
        "Final report: max survivable height, what absorbed the energy (connect to Unit 3: impact energy has to GO somewhere — crumple, stretch, or air resistance), and what v3 would change.",
     ],
     "check": "Slow-mo video + report with max height."},
    {"n": 29, "title": "Build Something the Family Needs", "time": "45 min",
     "hook": "Nothing needed — you're the engineer for a real client.",
     "steps": [
        "Real client, real problem: pick ONE — a phone stand for the homeschool desks, a resistance-band anchor organizer for the gym wall, a shoe/gear caddy, a watering funnel for the bean plants. Interview your \"client\" (Dad or Violet) for requirements.",
        "Design → build from scrap + Home Depot bits → get client feedback → improve once.",
        "This is the whole course in one mission: materials science (Unit 1), energy and forces, trade-offs (Unit 5), and iteration (Unit 8).",
     ],
     "check": "The thing exists, the client uses it, one improvement was made."},

    # ---- Capstone ----
    {"n": 30, "title": "The Lab Report & Science Showcase", "time": "60 min",
     "hook": "Nothing — today you close the lab out.",
     "note": "Close out your open experiments — the decomposition bags (Mission 26) and the sprout competition (Mission 23).",
     "steps": [
        "Close out open experiments: decomposition bags verdict (Mission 26), sprout competition result (Mission 23). Record final observations.",
        "Choose your best experiment of the course and write ONE full formal lab report (1 page): Question → Hypothesis → Materials → Procedure → Data (table or graph) → CER conclusion. This is the format every future science class will want.",
        "Showcase: demo your two favorite builds for Dad and Violet (the cooler? density tower? egg lander?) and explain the science in each.",
        "Big course question, answered out loud with examples: **\"How do matter and energy move through the world?\"** (Particles → reactions → heat flows → plates drift → resources form → life webs → cycles turn.)",
     ],
     "check": "Lab report complete + showcase delivered. COURSE COMPLETE — file the lab report in the PSA course-of-study record."},
]

UNIT_OF = {
    **{n: "Unit 1 · Matter & Particles" for n in range(1, 5)},
    **{n: "Unit 2 · Chemical Reactions" for n in range(5, 9)},
    **{n: "Unit 3 · Thermal Energy" for n in range(9, 13)},
    **{n: "Unit 4 · Tectonics & Rocks" for n in range(13, 17)},
    **{n: "Unit 5 · Natural Resources" for n in range(17, 20)},
    **{n: "Unit 6 · Ecosystems" for n in range(20, 24)},
    **{n: "Unit 7 · Cycling of Matter" for n in range(24, 27)},
    **{n: "Unit 8 · Engineering Design" for n in range(27, 30)},
    30: "Capstone",
}


def mission_blocks(m):
    before = []
    if m.get("adult"):
        before.append(f"⚠️ **ADULT ASSIST — {m['adult']}**")
    if m.get("prep"):
        before.append(f"⏰ **Prep the night before:** {m['prep']}")
    if m.get("note"):
        before.append(f"🔁 **Heads up:** {m['note']}")
    before.append(f"**Hook / lab:** {m['hook']}")
    before.append(SAFETY)
    return [
        (LessonBlock.KIND_MASTHEAD, {
            "eyebrow": f"Science · {UNIT_OF[m['n']]} · Mission {m['n']}",
            "title": m["title"],
            "thesis": f"About {m['time']}. Hook, run the experiment yourself, then write your CER.",
        }),
        (LessonBlock.KIND_PURPOSE, {"title": "Before you start", "paragraphs": before}),
        (LessonBlock.KIND_STEPS, {"title": "Do this",
                                  "steps": [{"detail": s} for s in m["steps"]]}),
        (LessonBlock.KIND_RECAP, {"title": "Show what you know", "items": COMPLETION_ITEMS}),
    ]


class Command(BaseCommand):
    help = "Seed Kaylin's Grade 7 Integrated Science mission course (idempotent, no AI)."

    def add_arguments(self, parser):
        parser.add_argument("--child-name", default="Kaylin")

    def handle(self, *args, **options):
        child = resolve_child(options["child_name"])
        curriculum = setup_course(child, SCIENCE_G7)
        for m in MISSIONS:
            upsert_mission(
                curriculum, child, m["n"],
                title=f"Mission {m['n']}: {m['title']}",
                intro=f"About {m['time']}.",
                parent_content=f"**Parent check:** {m['check']}\n\n{SAFETY}",
                blocks=mission_blocks(m),
            )
            add_journal(
                curriculum, child, m["n"],
                title=f"Mission {m['n']} · Lab Notebook",
                intro=JOURNAL_INTRO,
                questions=journal_questions(m),
            )
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(MISSIONS)} Science missions + lab notebooks (APPROVED) for "
            f"{child.first_name} — curriculum #{curriculum.pk}. Turning in the notebook "
            f"fires AI encouragement + a draft for you to stamp."
        ))
