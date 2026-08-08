"""Seed Violet's Grade 3 Science "mission" course into the app.

Same in-app, no-AI, no-new-UI pattern as the Social Studies courses (see
_mission_seed). Science adds per-mission flags folded into the "Before you start"
block: the standing safety rule on EVERY mission, a ⚠️ ADULT ASSIST banner where
the text flags it (Mission 22 hot water), ⏰ prep-the-night-before and 🔁 multi-day
"heads up" reminders. Completion = a LessonProgress 'done' mark. Mission text is
VERBATIM from the family's commissioned research build.

    python manage.py seed_sci_violet            # defaults to child "Violet"
"""
from django.core.management.base import BaseCommand

from curricula.blueprints import SCIENCE_G3
from tutor.models import LessonBlock

from ._mission_seed import add_journal, resolve_child, setup_course, upsert_mission

SAFETY = ("🛟 **Safety:** Water and mess are fine. Anything hot, sharp, or plugged in "
          "— get Dad first.")

# The RECAP block now points to the journal (a real place to write it), instead of
# just telling her to "tell or write" it with nowhere to put it.
COMPLETION_ITEMS = [
    "Open your **Science Log** below 👇 and write your **3 things** + a log sentence.",
    "**Turn it in** so Dad can read it and stamp your mission complete.",
    "**Snap a photo** of your experiment for your Work Log.",
]

JOURNAL_INTRO = (
    "Great work, scientist! 🔬 Write down what you discovered, then press **Turn in** "
    "so Dad can read your log and stamp this mission complete. Add your experiment photo "
    "to your Work Log too!"
)


def journal_questions(m):
    """Violet's science-log reflection for one mission: 3 things + a log sentence."""
    return [
        ("application",
         "**3 things I learned** — write three things you found out in this experiment.",
         "One short line for each — like a list. 1) … 2) … 3) …"),
        ("application",
         "**My science log** — what did you do, and what happened?",
         "Two or three sentences telling the story of your experiment."),
    ]

# n, title, time, watch, need, steps (VERBATIM), check; optional adult / prep / note.
MISSIONS = [
    # ---- Unit 1 — Forces & Motion (3-PS2) ----
    {"n": 1, "title": "Push It, Pull It", "time": "30 min",
     "watch": "**SciShow Kids** — search \"SciShow Kids force push pull\" (5 min).",
     "need": "paper, a marble, a straw, a bit of cardboard",
     "steps": [
        "Learn: A **force** is a push or a pull. Forces make things start moving, stop moving, speed up, slow down, or change direction.",
        "Force hunt: find 10 things in the apartment that move because of a push or pull (door, drawer, light switch, zipper, gym weights...). Make two lists: PUSH / PULL.",
        "Test: roll a marble across the floor. Make it (a) go faster, (b) turn, (c) stop — using only pushes and pulls from a straw blow, your finger, and a cardboard wall.",
     ],
     "check": "10-item list sorted correctly."},
    {"n": 2, "title": "The Great Ramp Races", "time": "40 min",
     "watch": "Nothing — straight to the lab!",
     "need": "cardboard or a paint stir stick, books, a toy car, tape, a ruler",
     "steps": [
        "Build a ramp from cardboard or a paint stir stick propped on books.",
        "**Experiment like a scientist:** race a toy car down the ramp at 3 heights (1 book, 3 books, 5 books). Mark where it stops each time with tape. Measure with a ruler.",
        "Make a results chart: height vs. distance. What's the pattern? (Higher ramp = bigger pull from gravity = faster = farther.)",
        "Prediction test: BEFORE you run 4 books, predict where the car will stop. Were you close?",
     ],
     "check": "Chart with 3 measured distances + her prediction."},
    {"n": 3, "title": "Friction — The Invisible Brake", "time": "35 min",
     "watch": "Search \"friction for kids video\" (any short one).",
     "need": "the ramp + car, a towel, sandpaper, foil, a ruler",
     "steps": [
        "Learn: **Friction** is a force that rubs against moving things and slows them down. Rough = more friction. Smooth = less.",
        "Experiment: same ramp, same car, same height — but change the landing surface: bare floor, towel, sandpaper, foil. Measure the stopping distance on each.",
        "Rank the surfaces from most slippery to grippiest. Where do you WANT friction (shoes, brakes, jiu-jitsu mats!) and where don't you (slides, sleds)?",
     ],
     "check": "4 surfaces ranked with measurements."},
    {"n": 4, "title": "Balloon Rocket", "time": "35 min",
     "watch": "Nothing needed — the steps show the setup.",
     "need": "a long string, a straw, a balloon, tape",
     "steps": [
        "Thread a long string through a straw. Tie the string tight across the room (chair to chair). Blow up a balloon, DON'T tie it, tape it to the straw, and let go!",
        "Learn: air pushes out the back → balloon pushes forward. Every action has an equal-and-opposite reaction (that's Newton's big idea — real rockets work exactly like this).",
        "Engineer it: test 2 changes (bigger balloon? steeper string? less air?). Which made it fly farthest?",
     ],
     "check": "Video/photo of a launch + which change worked best."},
    {"n": 5, "title": "Balanced vs. Unbalanced", "time": "30 min",
     "watch": "Search \"balanced and unbalanced forces for kids.\"",
     "need": "string, a toy, a bag of dried beans",
     "steps": [
        "Learn: When forces are **balanced**, nothing changes (tug-of-war tie). When **unbalanced**, motion changes (one side wins).",
        "Tabletop tug-of-war: tie string to a toy; you pull one end, hang a bag of beans from the other over the table edge. Add beans until the forces balance (toy sits still), then one more handful — unbalanced, it moves!",
        "Draw two pictures with force arrows: balanced (equal arrows) and unbalanced (one big arrow wins).",
     ],
     "check": "Both drawings have arrows the right sizes."},

    # ---- Unit 2 — Magnets & Static (3-PS2) ----
    {"n": 6, "title": "Magnet Detective", "time": "35 min",
     "watch": "**SciShow Kids** — search \"SciShow Kids magnets.\"",
     "need": "a magnet, 15 objects to test (coins, nails, foil, spoon, toys...)",
     "steps": [
        "Test 15 objects around home with a magnet: coins, fridge, nails, foil, spoon, toys, doorframe... Predict FIRST, then test. Two lists: STICKS / DOESN'T.",
        "Discover the rule: magnets grab things with **iron or steel** — not all metals! (Foil and most coins don't stick.)",
        "Poles test: put two magnets together both ways. Feel them snap together (**attract**) and push apart (**repel**) — a force you can feel but not see, with no touching!",
     ],
     "check": "15 predictions vs. results; she states the iron/steel rule."},
    {"n": 7, "title": "Force Through Walls", "time": "35 min",
     "watch": "Nothing needed.",
     "need": "a magnet, a nail, paper, cardboard, a book, foil, a cup of water, paperclips, string",
     "steps": [
        "Question: can magnetic force pass through stuff? Test: put a nail on the table, magnet UNDER the table — can you drag the nail around like a ghost? Now test through: paper (how many sheets?), cardboard, your hand, a book, foil, a cup of water.",
        "Make a \"magnet power chart\": material vs. did the force get through?",
        "Magnet fishing game: paperclip \"fish\" in a bowl of water, magnet on a string pole. Rescue all the fish without getting wet.",
     ],
     "check": "Power chart + ghost-drag video."},
    {"n": 8, "title": "Make a Compass", "time": "40 min",
     "watch": "Nothing needed.",
     "need": "a needle or paperclip, a magnet, a bottle cap, a bowl of water",
     "steps": [
        "Magnetize a needle or straightened paperclip: stroke it 30 times in ONE direction with your magnet.",
        "Tape it to a bottle cap and float it in a bowl of water. It slowly turns and points **north** — you built a compass, the same tool that guided ships for 1,000 years!",
        "Check it against Dad's phone compass. Then carry your bowl to a different room — does it still find north?",
     ],
     "check": "Photo of floating compass + phone comparison."},
    {"n": 9, "title": "Static Electricity — Lightning's Little Cousin", "time": "35 min",
     "watch": "Nothing needed.",
     "need": "a balloon, your hair or a fleece blanket, a faucet, tiny paper bits",
     "steps": [
        "Charge a balloon by rubbing it fast on your hair or a fleece blanket (20 rubs).",
        "Superpower tests: (a) stick the balloon to the wall, (b) make your hair reach up for it, (c) bend a thin stream of water from the faucet WITHOUT touching it, (d) make tiny paper bits jump up to the balloon.",
        "Learn: rubbing moves tiny **charges** onto the balloon; charges pull on things from a distance — just like magnets, a no-touch force. Lightning is this same thing, giant-sized.",
     ],
     "check": "Water-bending video (the best trick!)."},

    # ---- Unit 3 — Life Cycles (3-LS1) ----
    {"n": 10, "title": "Sprout Lab — Setup Day", "time": "30 min + daily 2-min checks",
     "watch": "**SciShow Kids** — search \"how does a seed become a plant.\"",
     "need": "2 ziplock bags, paper towels, 8 dried beans, tape",
     "steps": [
        "Fold a wet paper towel into a ziplock bag with 4 dried beans. Tape the bag to a sunny window.",
        "Make a second bag exactly the same but put it in a dark closet. **Same everything except light — that makes it a fair test.**",
        "Start your Sprout Journal: draw Day 0 for both bags. Check and draw every day for the next 2 weeks (2 minutes a day).",
     ],
     "note": "This is a MULTI-DAY lab — you'll come back to it in Mission 12. Draw both bags for 2 minutes every day until then.",
     "check": "Both bags set up + journal started."},
    {"n": 11, "title": "Every Living Thing Has a Cycle", "time": "35 min",
     "watch": "Search \"butterfly life cycle for kids\" and \"frog life cycle for kids.\"",
     "need": "paper, a brad or just draw the spinners",
     "steps": [
        "Learn the pattern ALL living things share: **born → grow → reproduce → die** — and around again. That's a **life cycle**.",
        "Make two spinner wheels (paper circle + brad or just drawn): butterfly (egg → caterpillar → chrysalis → butterfly) and frog (egg → tadpole → froglet → frog).",
        "Compare: which animal changes its whole body shape (**metamorphosis**) and which mostly just grows bigger? What about YOU?",
     ],
     "check": "Both wheels correct, in order."},
    {"n": 12, "title": "Sprout Lab — Results Day", "time": "30 min",
     "watch": "Open your Sprout Journal from Mission 10.",
     "need": "your two sprout bags, a ruler, a cup of soil",
     "steps": [
        "Open your Sprout Journal. Compare the window bag vs. the closet bag. Which sprouted better? Are the closet sprouts pale and weird? (Plants need light to make food!)",
        "Measure your longest sprout with a ruler. Add measurements to the journal.",
        "Plant the best sprouts in a cup of soil to keep the cycle going — your bean will grow, flower, and make NEW beans (reproduce!). Full circle.",
     ],
     "note": "Run this about a week after Mission 10, using the two bags you started then.",
     "check": "Journal shows both bags across days + measurement."},
    {"n": 13, "title": "Plant Life Cycle Wheel + Seed Hunt", "time": "30 min",
     "watch": "Nothing needed.",
     "need": "paper, and 5 real foods with seeds (apple, tomato, pepper, orange, beans...)",
     "steps": [
        "Make the plant life-cycle wheel: seed → sprout → plant → flower → fruit with new seeds → back to seed.",
        "Kitchen seed hunt: find seeds in 5 real foods (apple, tomato, pepper, orange, beans, cucumber...). Every seed = a plant's baby, packed with a lunchbox to start growing.",
        "Big idea out loud: why do plants make fruit at all? (To protect and spread their seeds!)",
     ],
     "check": "Wheel + 5 seeds found (photo of the seed lineup)."},

    # ---- Unit 4 — Traits & Families (3-LS3) ----
    {"n": 14, "title": "The Family Trait Lab", "time": "35 min",
     "watch": "Search \"inherited traits for kids\" (Generation Genius has a free one).",
     "need": "family members to survey, paper",
     "steps": [
        "Learn: **Traits** are features of a living thing. Many are **inherited** — passed from parents (eye color, hair, dimples). Others are **acquired** — learned or gained by living (jiu-jitsu skills, scars, language).",
        "Run a family trait survey on everyone you can (you, Kaylin, Dad, call a grandparent): can you roll your tongue? Attached or free earlobes? Right or left handed? Eye color? Chart everyone's answers.",
        "Find one trait you share with Dad and one that's different. Traits mix — that's why you're similar to family but not a copy!",
     ],
     "check": "Survey chart with at least 3 people."},
    {"n": 15, "title": "Inherited or Acquired?", "time": "30 min",
     "watch": "Nothing needed.",
     "need": "paper slips, a pen",
     "steps": [
        "Sort game: write these on slips and sort into INHERITED / ACQUIRED: eye color, speaking Spanish, freckles, a scar, curly hair, riding a bike, height (tricky — mostly inherited but food matters!), gymnastics skills, dimples, favorite color.",
        "Learn the twist: the **environment** can shape traits too. A plant with poor light grows pale (you SAW this in Sprout Lab!). Good food, sleep, and training shape how kids grow.",
        "Name 2 traits you're building right now through practice.",
     ],
     "check": "Sort mostly correct; she explains the height \"tricky\" one."},
    {"n": 16, "title": "Same Species, All Different", "time": "30 min",
     "watch": "Nothing needed.",
     "need": "10 leaves from one tree OR 10 beans from one bag, a ruler",
     "steps": [
        "Learn: Living things of the same kind still **vary** — no two dogs, leaves, or sisters are identical.",
        "Measure it: collect 10 leaves from the SAME tree or 10 beans from the same bag. Measure each with a ruler and line them up smallest → biggest. Draw the lineup.",
        "Think: could being a little bigger or smaller ever help one survive better? (Hold that thought — next unit!)",
     ],
     "check": "10 measured, ordered items (photo)."},

    # ---- Unit 5 — Survival, Adaptation & Fossils (3-LS4) ----
    {"n": 17, "title": "The Beak Buffet", "time": "40 min",
     "watch": "Nothing needed.",
     "need": "tweezers, spoon, clothespin, chopstick; rice, beans in water, cotton balls, marbles",
     "steps": [
        "You're a bird! Your \"beaks\": tweezers, spoon, clothespin, chopstick. Your \"foods\": rice grains, beans in a cup of water, cotton-ball \"bugs,\" marbles \"nuts.\"",
        "30 seconds per beak per food: count how many each beak collects. Fill in the results grid (4 beaks × 4 foods).",
        "Discover: every beak wins at SOMETHING. Birds' beak shapes match their food — that's an **adaptation**: a trait that helps a living thing survive in its home.",
        "Design-a-bird: draw an imaginary bird perfectly adapted to eat one food of your choice. Label its adaptations.",
     ],
     "check": "Results grid + labeled bird drawing."},
    {"n": 18, "title": "Camouflage Hunt", "time": "35 min",
     "watch": "Nothing needed.",
     "need": "newspaper/brown paper, bright paper, scissors, a helper",
     "steps": [
        "Cut 20 tiny paper \"moths\": 10 from newspaper/brown paper, 10 from bright pink/yellow paper. Have Dad or Kaylin scatter all 20 on a newspaper or the carpet while you look away.",
        "You get 15 seconds to grab all the moths you can spot. Count what you caught: bright vs. camouflaged.",
        "Learn: blending in (**camouflage**) is an adaptation — hidden moths survive and have hidden babies, so over time MORE moths look hidden. That's how nature \"chooses.\"",
     ],
     "check": "Catch counts show camouflage worked."},
    {"n": 19, "title": "Fossil Factory", "time": "40 min",
     "watch": "Search \"how fossils form for kids.\"",
     "need": "1 cup flour, ½ cup salt, ½ cup water; a shell, leaf, toy dino foot, LEGO",
     "steps": [
        "Make salt dough (1 cup flour + ½ cup salt + ½ cup water, knead).",
        "Press objects into dough discs: a shell, leaf, toy dinosaur foot, LEGO. Remove them — you've made **imprint fossils**. Let them dry hard (overnight).",
        "Learn: real fossils form when living things get buried in mud that slowly turns to stone over millions of years. Fossils are nature's photo album of creatures **long ago** — some, like dinosaurs, are **extinct** (gone forever).",
     ],
     "prep": "The fossils need to dry hard overnight — make them the day before you want to show them, and save some dough for Mission 20.",
     "check": "Fossil photos; she can say what a fossil is."},
    {"n": 20, "title": "Fossil Detective", "time": "35 min",
     "watch": "Nothing needed.",
     "need": "fresh salt dough, 3 mystery objects, a helper",
     "steps": [
        "Swap fossils: have Kaylin press 3 mystery objects into fresh dough while you're not looking. Now YOU'RE the paleontologist — examine each imprint and figure out what made it. Write your evidence.",
        "Habitat clues: if you found a fish fossil on a mountain, what does that tell you the mountain USED to be? (Underwater! Environments change over huge time.)",
        "Match game: draw lines — webbed feet→water, thick fur→cold, long neck→tall trees, sharp claws→hunting. Traits fit environments.",
     ],
     "check": "Mystery imprints identified with evidence stated."},

    # ---- Unit 6 — Weather, Climate & Hazards (3-ESS2/3) ----
    {"n": 21, "title": "Weather Station — Rain Gauge & Log", "time": "30 min setup + 1 min/day for a week",
     "watch": "**NASA Climate Kids** — [climatekids.nasa.gov](https://climatekids.nasa.gov) (browse \"Weather & Climate\").",
     "need": "a plastic bottle, a ruler-marked paper strip, tape, rocks",
     "steps": [
        "Build a rain gauge: cut the top off a plastic bottle, flip the top upside-down into the base as a funnel, tape a ruler-marked paper strip up the side. Set it outside or on the balcony, weighed with rocks.",
        "Start a 7-day Weather Log: every day record temperature (phone), sky (sun/clouds/rain), and gauge reading.",
        "Learn: **weather** = what the sky does TODAY. Scientists measure it every single day, just like you now.",
     ],
     "note": "This is a MULTI-DAY log — record it for 7 days and finish it in Mission 23.",
     "check": "Gauge deployed + log started."},
    {"n": 22, "title": "Cloud in a Jar", "time": "35 min",
     "watch": "Nothing needed.",
     "need": "a jar, warm water, ice cubes, a plate; hairspray or a match (Dad's job)",
     "adult": "Dad pours the hot (not boiling) water and handles the match smoke.",
     "steps": [
        "Have Dad pour hot (not boiling) water 1/3 up a jar. Swirl. Spray one puff of hairspray or hold a lit-then-blown-out match's smoke in (Dad's job), then put a plate of ice cubes on top.",
        "Watch a real cloud swirl inside! Learn the recipe: **warm wet air rises + cools + sticks to tiny particles = cloud**. Lift the plate and let your cloud escape.",
        "Cloud spotting: look outside or at pictures — puffy **cumulus**, streaky **cirrus**, gray blanket **stratus**. Draw all three.",
     ],
     "check": "Cloud jar video + 3 cloud types drawn."},
    {"n": 23, "title": "Weather vs. Climate", "time": "30 min",
     "watch": "Nothing needed.",
     "need": "paper, your Weather Log from Mission 21",
     "steps": [
        "Learn the difference: **Weather** = today's mood. **Climate** = a place's personality (what it's USUALLY like over many years). Sacramento's climate: hot dry summers, mild wet winters.",
        "Climate match: draw lines from place to climate — Sacramento→hot dry summer; Hawaii→warm and rainy; Alaska→long cold winter; Arizona desert→very hot, very dry.",
        "Finish your 7-day Weather Log from Mission 21. Circle the pattern: was this week normal for Sacramento's climate personality?",
     ],
     "note": "Bring the 7-day Weather Log you started in Mission 21 — you finish it here.",
     "check": "Completed log + match lines correct."},
    {"n": 24, "title": "Design vs. Disaster — Wind!", "time": "40 min",
     "watch": "Nothing needed.",
     "need": "paper, tape, a fan (or big lung power)",
     "steps": [
        "Learn: Some weather is dangerous — windstorms, floods, lightning. Engineers design to REDUCE the damage (3-ESS3!).",
        "Challenge: build a paper-and-tape house (max 20 min) that can survive the Fan Test — Dad's fan (or your biggest lung-power) at 2 feet for 10 seconds.",
        "If it flies away: study why, rebuild stronger (wide base? taped-down edges? triangle walls?), and re-test. Iterating is what real engineers do.",
     ],
     "check": "Fan test video (before/after if it needed a rebuild)."},
    {"n": 25, "title": "Flood Fighters", "time": "40 min",
     "watch": "Nothing needed.",
     "need": "a baking pan, foil, a sponge or dough, cotton balls, water",
     "steps": [
        "Learn: West Sacramento's biggest weather hazard is **flooding** — that's why our city has levees (you built these in social studies!).",
        "Build a river town in a baking pan: foil river channel, sponge or dough \"town\" beside it. Flood it with a big pour — disaster!",
        "Now engineer protection: rebuild with foil levees and a cotton-ball \"sandbag\" wall. Flood it again with the SAME pour. Did the town stay dry?",
        "Compare: which protection worked best? Real engineers protect our real town the same way.",
     ],
     "check": "Before/after flood videos."},

    # ---- Capstone ----
    {"n": 26, "title": "Violet's Science Fair", "time": "45 min",
     "watch": "Nothing — today you're the scientist on stage.",
     "need": "your 3 favorite experiments from the whole course",
     "steps": [
        "Pick your 3 favorite experiments from the whole course and set them up on the table: maybe the compass, the beak buffet, and the flood town?",
        "Run a Science Fair for Dad and Kaylin: demonstrate each one live and explain what force or science idea makes it work.",
        "Answer the big course question out loud: **\"What does a scientist do?\"** (Asks a question → predicts → tests fairly → measures → explains with evidence. You did that 25 times!)",
     ],
     "check": "Fair delivered; she explains all 3 demos. COURSE COMPLETE — log it in the PSA course-of-study record."},
]

UNIT_OF = {
    **{n: "Unit 1 · Forces & Motion" for n in range(1, 6)},
    **{n: "Unit 2 · Magnets & Static" for n in range(6, 10)},
    **{n: "Unit 3 · Life Cycles" for n in range(10, 14)},
    **{n: "Unit 4 · Traits & Families" for n in range(14, 17)},
    **{n: "Unit 5 · Adaptation & Fossils" for n in range(17, 21)},
    **{n: "Unit 6 · Weather & Climate" for n in range(21, 26)},
    26: "Capstone",
}


def mission_blocks(m):
    before = []
    if m.get("adult"):
        before.append(f"⚠️ **ADULT ASSIST — {m['adult']}**")
    if m.get("prep"):
        before.append(f"⏰ **Prep the night before:** {m['prep']}")
    if m.get("note"):
        before.append(f"🔁 **Heads up:** {m['note']}")
    before.append(f"**Watch first:** {m['watch']}")
    if m.get("need"):
        before.append(f"**You'll need:** {m['need']}")
    before.append(SAFETY)
    return [
        (LessonBlock.KIND_MASTHEAD, {
            "eyebrow": f"Science · {UNIT_OF[m['n']]} · Mission {m['n']}",
            "title": m["title"],
            "thesis": f"About {m['time']}. Watch, then DO the experiment, then show what you know.",
        }),
        (LessonBlock.KIND_PURPOSE, {"title": "Before you start", "paragraphs": before}),
        (LessonBlock.KIND_STEPS, {"title": "Do this",
                                  "steps": [{"detail": s} for s in m["steps"]]}),
        (LessonBlock.KIND_RECAP, {"title": "Show what you know", "items": COMPLETION_ITEMS}),
    ]


class Command(BaseCommand):
    help = "Seed Violet's Grade 3 Science mission course (idempotent, no AI)."

    def add_arguments(self, parser):
        parser.add_argument("--child-name", default="Violet")

    def handle(self, *args, **options):
        child = resolve_child(options["child_name"])
        curriculum = setup_course(child, SCIENCE_G3)
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
                title=f"Mission {m['n']} · Science Log",
                intro=JOURNAL_INTRO,
                questions=journal_questions(m),
            )
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(MISSIONS)} Science missions + journals (APPROVED) for "
            f"{child.first_name} — curriculum #{curriculum.pk}. Turning in the journal "
            f"fires AI encouragement + a draft for you to stamp."
        ))
