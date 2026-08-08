"""Seed Violet's Grade 3 Social Studies "mission" course into the app.

Self-contained + idempotent: ensures the Curriculum exists, applies the
SOCIAL_STUDIES_G3 blueprint (Units -> Missions), places Violet on it, and upserts
one APPROVED Material per mission built from LessonBlock rows. Each mission also
gets an **Explorer's Log** (a student journal QuestionSet, via add_journal): Violet
writes her 3 things + a log sentence and turns it in, which fires warm AI
encouragement + a DRAFT mastery assessment the parent reviews and stamps. The
journal is what lands in the charter record.

Mission text (steps, resource links, parent-check) is transcribed VERBATIM from
the family's commissioned research build; light markdown only. Resource URLs are
authored as markdown links (rendered by markdownify_inline) AND printed as plain
text so a printed page still shows the address.

    python manage.py seed_ss_violet            # defaults to child "Violet"
    python manage.py seed_ss_violet --child-name Violet
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from curricula.blueprints import SOCIAL_STUDIES_G3
from curricula.models import Curriculum, CurriculumPlacement, Lesson
from curricula.services import apply_blueprint
from students.models import Student
from tutor.models import LessonBlock, Material

from ._mission_seed import add_journal, linkify_searches, mission_quiz
from ._saxon_seed import validate_blocks

# The RECAP now points to the Explorer's Log (a real place to write it), instead of
# just telling her to "tell or write" it with nowhere to put it.
COMPLETION_ITEMS = [
    "Open your **Explorer's Log** below 👇 and write your **3 things** + a log sentence.",
    "**Turn it in** so Dad can read it and stamp your mission complete.",
    "**Snap a photo** of what you made for your Work Log.",
]

JOURNAL_INTRO = (
    "Explorer, log your discovery! 🧭 Write what you learned, then press **Turn in** so "
    "Dad can read your log and stamp this mission complete. Add your photo to your Work "
    "Log too!"
)


def journal_questions(m):
    """Violet's Explorer's Log reflection: 3 things + a log sentence."""
    return [
        ("application",
         "**3 things I learned** — write three things you found out on this mission.",
         "One short line for each — like a list. 1) … 2) … 3) …"),
        ("application",
         "**My log** — write one or two sentences about what you did today.",
         "Tell the story like an explorer writing in a journal."),
    ]

# Each mission: n, title, time, need (You'll need), watch (Watch/Read first — may
# hold a markdown link), steps (VERBATIM "Do this"), check (Parent check).
MISSIONS = [
    # ---- Unit 1 — Maps & Our Place (3.1) ----
    {"n": 1, "title": "Map Detective", "time": "35 min",
     "need": "paper, crayons/markers, a device with Google Maps",
     "watch": "Google Maps — search **\"West Sacramento, CA.\"** Zoom out slowly until you can see all of California.",
     "steps": [
        "Find on the map: your home, the Sacramento River, the American River, downtown Sacramento, the Sierra Nevada mountains (zoom east), the Pacific Ocean (zoom west).",
        "Draw your own map of your neighborhood on paper. Include: your home, one street name, one place you visit (park, store, gym).",
        "Add a **compass rose** (N, E, S, W) and a **map key** with at least 3 symbols.",
     ],
     "check": "Map has compass rose + key with 3 symbols."},
    {"n": 2, "title": "Landforms of Our Valley", "time": "35 min",
     "need": "salt dough or clay, toothpicks, small paper flags",
     "watch": "Search YouTube: **\"landforms for kids\"** (any short video, 5 min max).",
     "steps": [
        "Learn these words: **valley, river, delta, foothills, mountains**. Our home is in the **Central Valley** between two mountain ranges.",
        "Make a salt-dough or clay relief map of California: flat valley in the middle, mountains (Sierra Nevada) on the right/east, coast range on the left/west, and press a groove for the Sacramento River flowing down the valley.",
        "Label with toothpick flags: Valley, Sierra Nevada, Sacramento River, Delta, Pacific Ocean.",
     ],
     "check": "Relief map shows valley between two mountain ranges with river."},
    {"n": 3, "title": "Rivers Are Why We're Here", "time": "30 min",
     "need": "foil, a book, a cup of water, a baking pan",
     "watch": "Look at your relief map from Mission 2.",
     "steps": [
        "Answer out loud: Why do you think people built cities next to rivers? (Think: water, food, boats, farming.)",
        "On foil, shape a winding river channel about 2 feet long. Prop one end up on a book. Pour a slow cup of water down it into a baking pan. Watch how water flows downhill — just like the Sacramento River flows from the mountains to the ocean.",
        "Draw the path: mountains → river → delta → ocean.",
     ],
     "check": "She can explain that rivers flow downhill from mountains to the ocean and why cities grew next to them."},
    {"n": 4, "title": "People Change the Land", "time": "40 min",
     "need": "foil, cardboard, tape, water, a baking pan",
     "watch": "Search **\"Folsom Dam photo\"** — look at 2–3 pictures.",
     "steps": [
        "Learn: People near us changed the land with **levees** (walls of earth that hold rivers in) and **dams** (walls that hold water back). West Sacramento is protected by levees!",
        "Rebuild your foil river. This time, build a **dam** across it from a cardboard piece taped in place, and **levees** (rolled foil walls) along the sides. Pour water and test: does your dam hold back a lake? Do the levees stop flooding?",
        "Fix any leaks and test again — engineers always test twice.",
     ],
     "check": "Photo shows dam + levees on the model; she can say what each one does."},

    # ---- Unit 2 — First People: Nisenan & Miwok (3.2) ----
    {"n": 5, "title": "Who Lived Here First?", "time": "35 min",
     "need": "paper, crayons",
     "watch": "[Nisenan factcard](https://factcards.califa.org/cai/nisenan.html) — read it. "
              "https://factcards.califa.org/cai/nisenan.html",
     "steps": [
        "Learn: Long before any city, this land was home to the **Nisenan** (Southern Maidu) people north and east of the rivers, the **Plains Miwok** to the south, and the **Patwin** to the west.",
        "Trace or draw a simple map of the Sacramento area. Color three territory zones and label them: Nisenan, Plains Miwok, Patwin. Mark where YOUR home is — whose homeland do you live on?",
        "Say the three tribe names out loud three times so you remember them.",
     ],
     "check": "Territory map labeled with all three nations + home marked."},
    {"n": 6, "title": "Acorns & Salmon — Food from the Land", "time": "35 min",
     "need": "a small handful of oats, a bowl, a clean rock",
     "watch": "Re-read the \"food\" section of the [Nisenan factcard](https://factcards.califa.org/cai/nisenan.html).",
     "steps": [
        "Learn: The Nisenan gathered **acorns** from oak trees and ground them into flour, then rinsed out the bitterness with water. They caught **salmon** from the rivers.",
        "Try it: put a small handful of oats (pretend acorns) in a bowl. Grind them with a clean rock until they turn to flour. That's hard work — Nisenan kids helped do this every fall!",
        "Answer out loud: Why did the Nisenan live near rivers and oak trees? (Same reason cities came later — the land gave them what they needed.)",
     ],
     "check": "Photo of ground \"acorn flour\"; she connects food sources to geography."},
    {"n": 7, "title": "Build a Tule House", "time": "40 min",
     "need": "drinking straws or thin twigs, tape, cardboard, dry grass / raffia / cut paper",
     "watch": "Search images: **\"tule house Nisenan\"** or **\"California tule house.\"**",
     "steps": [
        "Learn: Nisenan homes were dome-shaped, made from **tule reeds** (tall marsh plants) tied over a bent-branch frame. Cool in summer, warm in winter — made 100% from local plants.",
        "Build a model: bend drinking straws or thin twigs into a dome frame, tape the base to cardboard, then layer dry grass, raffia, or cut paper strips over it like tule bundles.",
        "Compare out loud: What is your house made of? Where did those materials come from?",
     ],
     "check": "Photo of dome-shaped model house."},
    {"n": 8, "title": "Stories, Trade & Daily Life", "time": "30 min",
     "need": "a paper square, paper strips, scissors",
     "watch": "[Nisenan factcard](https://factcards.califa.org/cai/nisenan.html) sections on tools/culture.",
     "steps": [
        "Learn: The Nisenan made baskets so tightly woven they could hold water, traded goods with neighboring tribes, and passed down history through **spoken stories** (no writing needed — memory!).",
        "Weave a simple paper basket: cut slits in a paper square and weave paper strips over-under.",
        "Story challenge: listen to a parent or sister tell a 30-second story, then repeat it back as exactly as you can. That's how history traveled for thousands of years.",
     ],
     "check": "Paper weaving photo + she retells a short story."},
    {"n": 9, "title": "The Tribes Today — Wilton Rancheria", "time": "30 min",
     "need": "paper, crayons",
     "watch": "[Wilton Rancheria tribal history](https://wiltonrancheria-nsn.gov/about-us/tribal-history/) — "
              "read the opening paragraphs together. https://wiltonrancheria-nsn.gov/about-us/tribal-history/",
     "steps": [
        "Learn: Native people did not disappear. **Wilton Rancheria** is Sacramento County's only federally recognized tribe today, with hundreds of citizens who are Miwok and Nisenan people. They have their own tribal government — a chairperson and council, like a city has a mayor and council.",
        "Make a \"Then and Now\" poster: fold paper in half. Left side: draw Nisenan life long ago (tule house, acorns, river). Right side: draw the tribe today (tribal government building, modern citizens, cultural celebrations).",
     ],
     "check": "Poster shows past AND present — the key idea is continuity."},

    # ---- Unit 3 — Newcomers & Our Community's Story (3.3) ----
    {"n": 10, "title": "Sutter's Fort — Newcomers Arrive", "time": "35 min",
     "need": "craft sticks or cardboard, tape",
     "watch": "Search **\"Sutter's Fort virtual tour\"** or view photos at [suttersfort.org](https://suttersfort.org). https://suttersfort.org",
     "steps": [
        "Learn: In 1839, John Sutter built a fort and settlement called New Helvetia where Sacramento is now. Newcomers from around the world started arriving — this changed everything for the Nisenan and Miwok people, who lost most of their land.",
        "Build a fort: use craft sticks or cardboard to make a square fort with walls and a gate, like Sutter's Fort.",
        "Answer out loud: How do you think the Nisenan felt when newcomers took over their homeland? (There's no wrong feeling — this is a real, hard part of our history.)",
     ],
     "check": "Fort model photo + she can name Sutter's Fort and say arrival of settlers changed life for Native people."},
    {"n": 11, "title": "Gold!", "time": "35 min",
     "need": "a pan, dry rice or sand, 5 yellow beads or foil balls",
     "watch": "Search YouTube: **\"California Gold Rush for kids\"** (short video).",
     "steps": [
        "Learn: In 1848, gold was found near here. In one year, tens of thousands of people rushed to California from all over the world — the **Gold Rush**. Sacramento boomed as the supply town where miners bought food and tools.",
        "Gold panning game: put 5 small yellow beads or foil balls (\"gold\") in a pan of dry rice or sand. Shake and swirl to find them, like panning in a river.",
        "Think like a merchant: miners needed shovels, food, and tents. Who do you think got rich — most miners, or the people selling supplies? (Answer: the sellers!)",
     ],
     "check": "She can say what the Gold Rush was and why Sacramento grew from it."},
    {"n": 12, "title": "Capital City & the Railroad", "time": "35 min",
     "need": "yarn, craft sticks, tape",
     "watch": "Search images: **\"California State Capitol building\"** and **\"transcontinental railroad Sacramento.\"**",
     "steps": [
        "Learn: Sacramento became California's **capital city** — where state laws are made. Then in the 1860s, the **transcontinental railroad** started right here in Sacramento and connected California to the rest of the country.",
        "Build a railroad: lay two parallel yarn \"rails\" across the floor and tape craft-stick \"ties\" across them. How long can you make your track?",
        "Answer out loud: Before the railroad, a trip east took months by wagon. After, about a week by train. How would that change a city?",
     ],
     "check": "Track photo + she knows Sacramento = state capital + railroad starting point."},
    {"n": 13, "title": "Then vs. Now", "time": "35 min",
     "need": "paper, crayons, a parent's phone",
     "watch": "With a parent's phone, look up one old photo of Sacramento on [calisphere.org](https://calisphere.org) "
              "(search **\"Sacramento 1900\"**). https://calisphere.org",
     "steps": [
        "Compare the old photo to today: What's the same (river, some buildings, street layout)? What's different (cars, clothes, height of buildings)?",
        "Make a \"Then vs. Now\" drawing: same street corner, drawn twice — once as the old photo shows, once as today.",
        "Learn the word **primary source**: a photo, letter, map, or object made at the time in history. Old photos are primary sources — evidence, like clues!",
     ],
     "check": "Drawing pair + she can define \"primary source.\""},
    {"n": 14, "title": "Oral History Interview", "time": "30 min",
     "need": "paper and pencil, or a device to record",
     "watch": "Nothing — YOU are the historian today.",
     "steps": [
        "Interview your dad (or grandparent by phone) with these 4 questions: Where did you grow up? What did kids do for fun? What did school look like? What's one big way the world changed since you were my age?",
        "Write down (or record) the best answer.",
        "Learn: An interview with someone who lived through history is an **oral history** — a primary source you just created!",
     ],
     "check": "She asked all 4 questions and recorded one answer."},

    # ---- Unit 4 — Rules, Government & Citizenship (3.4) ----
    {"n": 15, "title": "Why Rules?", "time": "30 min",
     "need": "a card or board game",
     "watch": "None needed.",
     "steps": [
        "Play a card or board game for 5 minutes with NO rules — everyone does whatever they want. (It falls apart fast!)",
        "Now play with the real rules. Which was more fun and fair?",
        "Learn: Communities need **laws** (rules for everyone) so life is safe and fair. People who break laws face **consequences**, just like in games.",
        "List 3 laws you know (examples: wear a seatbelt, stop at red lights, don't take what isn't yours).",
     ],
     "check": "She explains why the no-rules game failed and names 3 real laws."},
    {"n": 16, "title": "The Constitution — Our Rulebook", "time": "35 min",
     "need": "paper, a fancy pen",
     "watch": "[Ben's Guide to the U.S. Government](https://bensguide.gpo.gov) — click the Apprentice (ages 4–8) or "
              "Journeyman level, read about the Constitution. https://bensguide.gpo.gov",
     "steps": [
        "Learn: The **U.S. Constitution** is the rulebook for our whole country — the highest law. It says what the government can do and protects our rights.",
        "Write a **Family Constitution**: with fancy lettering, write 5 rules your household agrees to (be kind, tell the truth, clean up your gear, etc.). Everyone signs it. Post it on the wall.",
     ],
     "check": "Signed Family Constitution posted."},
    {"n": 17, "title": "Three Branches — the Three-Legged Stool", "time": "35 min",
     "need": "clay, 3 craft sticks or straws",
     "watch": "[Ben's Guide](https://bensguide.gpo.gov) — \"Branches of Government.\" https://bensguide.gpo.gov",
     "steps": [
        "Learn the three branches: **Legislative** (makes laws — Congress), **Executive** (carries out laws — President), **Judicial** (judges laws — courts). Three branches share power so no one gets too much — like a stool that needs all three legs.",
        "Build a three-legged stool from clay + 3 craft sticks (or straws). Label each leg with a branch. Try balancing it on 2 legs — it tips! All three are needed.",
     ],
     "check": "Stool photo with legs labeled; she names all three branches."},
    {"n": 18, "title": "Our Local Government", "time": "30 min",
     "need": "paper, crayons, a device to look up the mayor",
     "watch": "With a parent, look up: **\"Who is the mayor of West Sacramento?\"**",
     "steps": [
        "Learn: Cities have their own small governments — a **mayor** and **city council** make local rules (parks, streets, libraries). The **county** and **state** handle bigger things.",
        "Draw a pyramid with 3 levels: City (bottom — closest to you), State (middle — Sacramento Capitol), Country (top — Washington D.C.). Add one thing each level takes care of.",
        "City council challenge: If YOU were on the city council, what one thing would you improve in West Sacramento? Draw your idea.",
     ],
     "check": "Pyramid + her improvement idea."},
    {"n": 19, "title": "Symbols & Heroes", "time": "35 min",
     "need": "an index card, crayons",
     "watch": "Search images: American flag, bald eagle, Statue of Liberty, Liberty Bell, California grizzly bear flag.",
     "steps": [
        "Learn what each symbol stands for (flag = 50 states/13 colonies; eagle = strength and freedom; Statue of Liberty = welcome; bear flag = California).",
        "Pick ONE American hero: Abraham Lincoln, Harriet Tubman, Frederick Douglass, Benjamin Franklin, or Martin Luther King Jr. Look up 3 facts about them.",
        "Make a hero trading card: their picture (drawn), name, and 3 facts on an index card.",
     ],
     "check": "Trading card with 3 accurate facts."},

    # ---- Unit 5 — Our Local Economy (3.5) ----
    {"n": 20, "title": "Goods & Services", "time": "30 min",
     "need": "paper slips, a pen",
     "watch": "None needed.",
     "steps": [
        "Learn: **Goods** are things you can hold (food, toys, shoes). **Services** are work people do for you (haircut, doctor, jiu-jitsu coach!). **Producers** make/do them; **consumers** buy/use them.",
        "Sort game: write these on slips and sort into two piles — apple, dentist visit, soccer ball, car wash, book, gymnastics class, bread, mail delivery, headphones, haircut.",
        "Name 2 times YOU were a consumer this week, and 1 way you could be a producer.",
     ],
     "check": "All 10 slips sorted correctly."},
    {"n": 21, "title": "Resources of Our Region", "time": "35 min",
     "need": "paper, crayons",
     "watch": "Search images: **\"Port of West Sacramento\"** and **\"Sacramento Valley farms.\"**",
     "steps": [
        "Learn three kinds of resources: **Natural** (rivers, rich valley soil, sunshine), **Human** (workers, farmers, teachers — and their skills!), **Capital** (tools, tractors, the Port, railroads).",
        "Our region's superpower: some of the best farmland in the world — rice, tomatoes, almonds — plus a river port that ships goods out.",
        "Make a resources poster: divide paper in 3 columns (Natural / Human / Capital) and draw 2 local examples in each.",
        "Big idea: When you do school, you're building YOUR human capital — skills that will be valuable someday.",
     ],
     "check": "Poster with 2 correct examples per column."},
    {"n": 22, "title": "Where Was It Made?", "time": "30 min",
     "need": "8 household items with labels, a world map or list",
     "watch": "None needed.",
     "steps": [
        "Scavenger hunt: find 8 items at home and read their labels — where was each made? (Check clothes tags, food packages, electronics.)",
        "Mark each country on a world map printout or list them by continent.",
        "Learn: Communities **trade** — we can't make everything ourselves, so we buy from other places and sell them what WE make (like Valley rice and almonds, which ship around the world!).",
     ],
     "check": "List of 8 items + origins; she can explain why places trade."},
    {"n": 23, "title": "Lemonade Stand Math", "time": "35 min",
     "need": "paper, a pencil",
     "watch": "None needed.",
     "steps": [
        "Plan a pretend lemonade stand. **Costs**: lemons $4, sugar $2, cups $2 = $6 total. You can make 20 cups.",
        "Decide your price per cup. Calculate: (price × 20) − $6 = your **profit**.",
        "Try 3 different prices. What happens at 25¢ (loss!), 50¢, $1? What price would customers actually pay?",
        "Learn: Every business balances **costs**, **price**, and what customers will pay. Choices have **trade-offs**.",
     ],
     "check": "Profit calculated correctly for at least 2 prices."},

    # ---- Capstone (3.1–3.5) ----
    {"n": 24, "title": "History Museum Day", "time": "45 min + optional field trip",
     "need": "everything you made this course",
     "watch": "Nothing — today you are the museum guide.",
     "steps": [
        "Set up a \"museum\" on the kitchen table with everything you made: maps, relief map, tule house, fort, stool, posters, trading card.",
        "Give Dad and your sister a 5-minute museum tour. For each exhibit, say one thing it taught you.",
        "Answer the big course question: **\"How has our community changed, and what has stayed the same?\"** (River and land are still here; the people, buildings, and jobs changed; the Nisenan and Miwok were here first and are STILL here.)",
        "**Optional field trip** (counts as a bonus session): Sutter's Fort SHP, California State Indian Museum, State Capitol Museum (free), or California State Railroad Museum Homeschool Day.",
     ],
     "check": "She gives the tour and answers the big question. COURSE COMPLETE — log it in the PSA course-of-study record."},
]

UNIT_OF = {  # mission number -> (unit label) for the masthead eyebrow
    **{n: "Unit 1 · Maps & Our Place" for n in range(1, 5)},
    **{n: "Unit 2 · First People" for n in range(5, 10)},
    **{n: "Unit 3 · Our Community's Story" for n in range(10, 15)},
    **{n: "Unit 4 · Rules & Government" for n in range(15, 20)},
    **{n: "Unit 5 · Our Local Economy" for n in range(20, 24)},
    24: "Capstone",
}


def mission_blocks(m):
    """Build the uniform mission Material from a mission dict."""
    before = []
    if m.get("need"):
        before.append(f"**You'll need:** {m['need']}")
    before.append(f"**Watch / Read first:** {linkify_searches(m['watch'])}")
    return [
        (LessonBlock.KIND_MASTHEAD, {
            "eyebrow": f"Social Studies · {UNIT_OF[m['n']]} · Mission {m['n']}",
            "title": m["title"],
            "thesis": f"About {m['time']}. Read it, do it, then show what you know.",
        }),
        (LessonBlock.KIND_PURPOSE, {
            "title": "Before you start",
            "paragraphs": before,
        }),
        (LessonBlock.KIND_STEPS, {
            "title": "Do this",
            "steps": [{"detail": s} for s in m["steps"]],
        }),
        (LessonBlock.KIND_RECAP, {
            "title": "Show what you know",
            "items": COMPLETION_ITEMS,
        }),
    ]


class Command(BaseCommand):
    help = "Seed Violet's Grade 3 Social Studies mission course (idempotent, no AI)."

    def add_arguments(self, parser):
        parser.add_argument("--child-name", default="Violet",
                            help="Child first name to build the course for.")

    def handle(self, *args, **options):
        name = options["child_name"]
        child = Student.objects.filter(first_name__iexact=name).order_by("pk").first()
        if child is None:
            raise CommandError(f"No student named {name!r} found.")

        # 1. Ensure the Curriculum exists (idempotent by parent + name).
        curriculum, made = Curriculum.objects.get_or_create(
            parent=child.parent,
            name=SOCIAL_STUDIES_G3["name"],
            defaults={
                "family": child.family,
                "subject": SOCIAL_STUDIES_G3["subject"],
                "grade_level": SOCIAL_STUDIES_G3["grade_level"],
            },
        )
        self.stdout.write(("Created" if made else "Found") + f" curriculum #{curriculum.pk} '{curriculum.name}'.")

        # 2. Apply the blueprint (Units -> Missions). Idempotent.
        apply_blueprint(curriculum, SOCIAL_STUDIES_G3)

        # 3. Place the child on it so the subject shows on her portal.
        CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum, defaults={"is_active": True})

        # 4. Upsert one APPROVED Material per mission.
        seeded = 0
        for m in MISSIONS:
            blocks = mission_blocks(m)
            validate_blocks(blocks)
            lesson = Lesson.objects.filter(
                chapter__curriculum=curriculum, number=m["n"]).first()
            if lesson is None:
                raise CommandError(f"Mission {m['n']} lesson not found — blueprint not applied?")
            material, created = Material.objects.get_or_create(
                lesson=lesson, skill_type=Material.SKILL_LESSON,
                defaults={
                    "title": f"Mission {m['n']}: {m['title']}",
                    "student_intro": f"About {m['time']}.",
                    "student_content": f"About {m['time']}.",
                    "parent_content": f"**Parent check:** {m['check']}",
                    "child": child,
                    "family": curriculum.family,
                    "status": Material.APPROVED,
                    "approved_at": timezone.now(),
                },
            )
            if not created:
                material.title = f"Mission {m['n']}: {m['title']}"
                material.parent_content = f"**Parent check:** {m['check']}"
                material.child = material.child or child
                if material.status != Material.APPROVED:
                    material.status = Material.APPROVED
                    material.approved_at = timezone.now()
                material.save()
            # Rewrite blocks in order.
            for order, (kind, data) in enumerate(blocks, start=1):
                LessonBlock.objects.update_or_create(
                    material=material, order=order, defaults={"kind": kind, "data": data})
            LessonBlock.objects.filter(material=material, order__gt=len(blocks)).delete()
            add_journal(
                curriculum, child, m["n"],
                title=f"Mission {m['n']} · Explorer's Log",
                intro=JOURNAL_INTRO,
                questions=journal_questions(m),
                quiz=mission_quiz("ss_violet", m["n"]),
            )
            seeded += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {seeded} missions + Explorer's Logs (APPROVED) for "
            f"{child.first_name} — curriculum #{curriculum.pk}. Turning in the log fires "
            f"AI encouragement + a draft for you to stamp."
        ))
