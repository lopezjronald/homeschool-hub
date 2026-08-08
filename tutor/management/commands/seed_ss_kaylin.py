"""Seed Kaylin's Grade 7 World History "mission" course into the app.

Same integration pattern as seed_ss_violet (self-contained + idempotent): ensure the
Curriculum, apply the WORLD_HISTORY_G7 blueprint, place Kaylin, and upsert one
APPROVED Material per mission from uniform LessonBlocks. Kaylin's course runs a
course-long WALL TIMELINE, so each mission's completion block lists the dated
timeline card(s) to add. Each mission also gets a **History Log** (a student journal
QuestionSet, via add_journal): Kaylin writes the Big Idea + 3 facts and turns it in,
which fires AI encouragement + a DRAFT assessment the parent reviews and stamps.

Mission text is transcribed VERBATIM from the family's commissioned research build.
Per the build rules, "search / Crash Course #N / Khan Academy" resources render as
bold search instructions (no fabricated links); real URLs are markdown links.

    python manage.py seed_ss_kaylin            # defaults to child "Kaylin"
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from curricula.blueprints import WORLD_HISTORY_G7
from curricula.models import Curriculum, CurriculumPlacement, Lesson
from curricula.services import apply_blueprint
from students.models import Student
from tutor.models import LessonBlock, Material

from ._mission_seed import add_journal, mission_quiz
from ._saxon_seed import validate_blocks

JOURNAL_INTRO = (
    "Historian, record what you found. 📜 Write the Big Idea and 3 facts in your own "
    "words, then press **Turn in** so Dad can review it and stamp this mission complete. "
    "Add a timeline/build photo to your Work Log too."
)


def journal_questions(m):
    """Kaylin's History Log reflection: the mission Big Idea + 3 facts."""
    return [
        ("application",
         "**Big Idea** — write this mission's big idea in one sentence, in your own words.",
         "What's the one thing a historian should take away from this mission?"),
        ("application",
         "**3 facts I learned** in this mission.",
         "One clear sentence each — names, dates, or ideas that stuck with you."),
    ]

# Each mission: n, title, time, watch (Read/Watch — markdown), steps (VERBATIM "Do"),
# cards (timeline card text for the completion block), check (Parent check).
MISSIONS = [
    # ---- Unit 1 — Rome Falls, Byzantium Rises (7.1) ----
    {"n": 1, "title": "Set Up + Why Rome Fell", "time": "45 min",
     "watch": "**Crash Course World History #12 \"Fall of the Roman Empire\"** (YouTube, ~12 min).",
     "steps": [
        "Build the wall timeline: tape a line across your wall/hallway, mark centuries from 300 to 1800 CE. Make 15 blank event cards for future missions.",
        "As you watch, list at least 4 reasons Rome weakened (ideas: too big to defend, invasions, weak/greedy leaders, economic trouble, empire split East/West).",
        "Rank your 4 reasons from most to least important and defend your #1 pick in 2 sentences.",
     ],
     "cards": "\"476 CE — Western Rome falls.\"",
     "check": "Timeline is up; she defends her top reason."},
    {"n": 2, "title": "Byzantium — Rome Lives On in the East", "time": "40 min",
     "watch": "**Khan Academy** — search \"Byzantine Empire overview\"; view images of the **Hagia Sophia**.",
     "steps": [
        "Learn: The eastern half of the empire survived nearly 1,000 more years as the **Byzantine Empire**, capital **Constantinople**. Emperor **Justinian** wrote down Roman laws in **Justinian's Code** — the ancestor of many modern legal systems.",
        "Build a dome: the Hagia Sophia's giant dome amazed the world. Engineer your own — build the widest free-standing dome/arch you can from craft sticks or cards. Test how much weight it holds (stack coins).",
        "Write: 2 things the Byzantines preserved from Rome (laws, Greek/Roman learning, Christianity in the East).",
     ],
     "cards": "\"537 CE — Hagia Sophia built.\"",
     "check": "Dome photo + 2 preservation facts."},
    {"n": 3, "title": "One Empire, Two Churches", "time": "35 min",
     "watch": "**CKHG World History** — chapter on Byzantium / the Christian church split. "
              "[Free PDFs](https://www.coreknowledge.org/free-resource/world-history/)",
     "steps": [
        "Learn: Over centuries, Christianity split into **Roman Catholic** (West, led by the Pope) and **Eastern Orthodox** (East, led by the Patriarch) — the **Great Schism of 1054**.",
        "Make a T-chart comparing West vs. East around 800 CE: language (Latin/Greek), church leader, capital, what daily life was like.",
        "Map task: on a Europe/Mediterranean map, shade the old Western Empire one color and the Byzantine East another.",
     ],
     "cards": "\"1054 — Great Schism.\"",
     "check": "T-chart with 4 accurate rows."},

    # ---- Unit 2 — The World of Islam (7.2) ----
    {"n": 4, "title": "Arabia — Crossroads of Trade", "time": "40 min",
     "watch": "**CKHG \"The Rise of Islam\"** opening chapters; **Crash Course World History #13 "
              "\"Islam, the Quran, and the Five Pillars.\"**",
     "steps": [
        "Learn: The Arabian Peninsula = mostly desert, so people lived by **trade caravans** and around **oases**; Mecca was a trade + religious hub. In the 600s, **Muhammad** began teaching Islam there; its holy book is the **Qur'an**.",
        "List the **Five Pillars of Islam** (faith, prayer, charity, fasting, pilgrimage) with a 5-finger hand-trace diagram — one pillar per finger.",
        "Map: on a blank map, label Arabia, Mecca, Medina, the Red Sea, the Persian Gulf.",
     ],
     "cards": "\"622 CE — the Hijra (Muhammad to Medina).\"",
     "check": "Hand diagram with all 5 pillars."},
    {"n": 5, "title": "An Empire in a Century", "time": "40 min",
     "watch": "**Khan Academy** — \"Spread of Islam.\"",
     "steps": [
        "Learn: Within ~100 years of Muhammad's death, Muslim rule stretched from Spain to India — under the **Umayyad** then **Abbasid** caliphates (a **caliph** = ruler).",
        "Yarn-map the expansion: on a printed map, lay yarn along the empire's edge at 632, then 750. Color the difference.",
        "Answer in 3 sentences: What helped Islam spread so fast? (Strong armies, fair treatment of conquered peoples, trade routes, a clear shared faith.)",
     ],
     "cards": "\"750 CE — Abbasid caliphate begins.\"",
     "check": "Two-stage expansion map."},
    {"n": 6, "title": "The Golden Age — House of Wisdom", "time": "45 min",
     "watch": "Search **\"Islamic Golden Age inventions kids.\"**",
     "steps": [
        "Learn: Baghdad's **House of Wisdom** gathered scholars who preserved Greek texts and pushed knowledge forward: **al-Khwarizmi** invented **algebra** (yes — the algebra you're doing in Saxon is named from Arabic *al-jabr*!), plus advances in medicine, astronomy, optics, and our number system (Arabic numerals with zero).",
        "Try it: write 247 in Roman numerals (CCXLVII), then multiply CCXLVII × XII without converting. Painful, right? Now do 247 × 12 in Arabic numerals. Write 2 sentences on why the number system mattered.",
        "Make a \"Golden Age Top 5\" ranked list of contributions with one sentence each.",
     ],
     "cards": "\"~830 CE — House of Wisdom flourishes.\"",
     "check": "The numeral comparison + Top 5 list."},
    {"n": 7, "title": "Trade Ties the World Together", "time": "40 min",
     "watch": "**CKHG** chapter on Muslim trade networks.",
     "steps": [
        "Learn: Muslim merchants linked Africa, Europe, and Asia by land and sea. Trade moved goods (silk, spices, gold, salt) AND ideas (numbers, paper, religion).",
        "Trade simulation solo game: make 6 city cards (Córdoba, Cairo, Baghdad, Timbuktu, Constantinople, Guangzhou) and 6 goods cards. Deal randomly; then \"travel\" between cities trading until each city holds the good it wants. Count your moves — trade takes networks!",
        "Write the unit Big Idea: how did the Islamic world connect three continents?",
     ],
     "cards": "one card of your choice from this unit.",
     "check": "Big Idea sentence names goods + ideas moving on trade routes."},

    # ---- Unit 3 — Medieval Europe (7.6) ----
    {"n": 8, "title": "Feudalism — The Pyramid of Power", "time": "40 min",
     "watch": "**Crash Course World History #14 \"The Dark Ages\"**; **CKHG** medieval Europe chapters.",
     "steps": [
        "Learn: After Rome fell, Europe fragmented. **Feudalism** organized society: king → lords/nobles → knights → peasants/serfs. Land was traded for loyalty and protection. The **manor** was a self-sufficient farm-village world.",
        "Build the pyramid: cardboard or craft-stick pyramid with 4 labeled levels; add one sentence per level about what that group gave and got.",
        "Learn **Charlemagne** (crowned 800 CE — briefly reunited much of Europe and revived learning).",
     ],
     "cards": "\"800 CE — Charlemagne crowned.\"",
     "check": "Pyramid with give/get labeled at all 4 levels."},
    {"n": 9, "title": "The Church at the Center", "time": "40 min",
     "watch": "**CKHG** chapter on the medieval Church; images of illuminated manuscripts.",
     "steps": [
        "Learn: The Catholic Church was the most powerful institution in medieval Europe — it ran schools, crowned kings, and touched every life event. **Monasteries** preserved books by hand-copying them; monks decorated pages as **illuminated manuscripts**.",
        "Make your own illuminated page: choose a favorite quote or your name; write it in fancy lettering with a large decorated first letter, gold accents (yellow marker/foil), and a border.",
        "Answer: why did hand-copying make books rare and expensive — and who controlled knowledge as a result?",
     ],
     "cards": "your choice (e.g., \"910 — Cluny monastery founded\").",
     "check": "Illuminated page photo."},
    {"n": 10, "title": "Crusades & Magna Carta", "time": "45 min",
     "watch": "**Crash Course World History #15 \"The Crusades\"**; **Khan Academy \"Magna Carta.\"**",
     "steps": [
        "Learn: The **Crusades** (1096–1291) were wars where European Christians tried to take Jerusalem from Muslim rule. Military result: mostly failure. Side effects: trade with the East exploded, new ideas and goods flowed into Europe, kings gained power.",
        "Learn: In **1215**, English nobles forced King John to sign the **Magna Carta** — the king is UNDER the law, not above it. This idea flows straight into the U.S. Constitution.",
        "Cause-effect chain: draw arrows — Crusades → more trade → towns and merchants grow → feudalism weakens. Add one sentence per arrow.",
     ],
     "cards": "\"1096 — First Crusade\" and \"1215 — Magna Carta.\"",
     "check": "Cause-effect chain makes sense; she can state the Magna Carta's big idea."},
    {"n": 11, "title": "The Black Death", "time": "40 min",
     "watch": "Search **Khan Academy / Crash Course \"Black Death.\"**",
     "steps": [
        "Learn: In 1347–1351 the **bubonic plague** arrived on trade ships and killed roughly **one-third of Europe**. Workers became scarce → surviving peasants could demand pay → serfdom crumbled → feudalism began to die.",
        "Simulation with rice or beans: lay out 30 = a village. Remove 10. Now list village jobs (farmer, miller, blacksmith, priest...) — who does the missing work? What would YOU demand to do two jobs?",
        "Write 3 sentences: how a disaster accidentally gave common people more power.",
     ],
     "cards": "\"1347 — Black Death reaches Europe.\"",
     "check": "Her 3 sentences link plague → labor shortage → workers' power."},

    # ---- Unit 4 — Imperial China: Tang & Song (7.3) ----
    {"n": 12, "title": "The Exam That Ran an Empire", "time": "40 min",
     "watch": "**Crash Course World History #7** (China) + **Khan Academy \"Tang and Song China.\"**",
     "steps": [
        "Learn: While Europe fragmented, China reunified under the **Tang** then **Song** dynasties — the most advanced civilization on Earth at the time. Government jobs went to men who passed the brutal **civil service exam** on Confucian texts — talent (partly) over birth.",
        "Compare: make a two-column chart — \"How you got power in medieval Europe\" (born noble) vs. \"in Song China\" (pass the exam). Which is fairer? Which is closer to today?",
        "Mini-exam experience: memorize a 4-line poem in 10 minutes, then write it perfectly from memory. Exam candidates memorized entire books.",
     ],
     "cards": "\"618 — Tang dynasty begins.\"",
     "check": "Comparison chart + recited poem."},
    {"n": 13, "title": "Invented in China", "time": "45 min",
     "watch": "Search **\"Four Great Inventions of China.\"**",
     "steps": [
        "Learn the four giants: **paper, printing, gunpowder, the magnetic compass** — plus paper money, porcelain, and mechanical clocks. Each one later transformed the whole world.",
        "Build a working compass: magnetize a needle (stroke it 30× one direction with a fridge magnet), tape it to a bottle-cap raft, float it in a bowl. It finds north! Check it against a phone compass.",
        "Rank the four inventions by world impact and defend your #1 in 3 sentences.",
     ],
     "cards": "\"~1040 — movable type printing in China.\"",
     "check": "Compass works (photo/video) + ranked list."},
    {"n": 14, "title": "Silk Road & the Mongols", "time": "40 min",
     "watch": "**Crash Course World History #9 \"The Silk Road\"** and **#17 \"The Mongols.\"**",
     "steps": [
        "Learn: The **Silk Road** carried silk, porcelain, and ideas between China and the West. In the 1200s **Genghis Khan** built the largest land empire ever; his grandson **Kublai Khan** ruled China, where **Marco Polo** visited and amazed Europe with his reports.",
        "Map: draw the Silk Road route Chang'an → Samarkand → Baghdad → Constantinople with yarn on your map.",
        "Two-sided argument (3 sentences each): \"The Mongols were destroyers\" vs. \"The Mongols connected the world\" (safe roads, trade revival, idea exchange). Both are true — historians call this complexity.",
     ],
     "cards": "\"1206 — Genghis Khan unites the Mongols.\"",
     "check": "Both arguments written."},

    # ---- Unit 5 — Medieval Japan (7.5) ----
    {"n": 15, "title": "Islands That Borrowed and Made It Their Own", "time": "40 min",
     "watch": "**CKHG \"Medieval Japan\"** opening; **Khan Academy** Japan overview.",
     "steps": [
        "Learn: Japan = mountainous islands near China. Japan borrowed writing, Buddhism, and government ideas from China — then reshaped them into its own culture. Native **Shinto** (spirits in nature) blended with **Buddhism**.",
        "Geography analysis: list 3 ways island geography shaped Japan (protection from invasion — the Mongols failed twice; seafood diet; strong regional clans in mountain valleys).",
        "Culture sort: make cards — writing system, Buddhism, Shinto, tea ceremony, government ranks — and sort: \"borrowed from China\" vs. \"homegrown.\"",
     ],
     "cards": "\"1274 — Mongol invasion of Japan fails.\"",
     "check": "Sort is accurate; 3 geography effects listed."},
    {"n": 16, "title": "Shoguns & Samurai", "time": "45 min",
     "watch": "Search **\"feudal Japan shogun samurai for students.\"**",
     "steps": [
        "Learn: Real power belonged to the **shogun** (military ruler), not the emperor. **Samurai** warriors served lords (**daimyo**) and followed **bushido** — a code of loyalty, courage, and honor. Sound familiar? Compare to European knights and chivalry.",
        "Double pyramid: draw Japan's feudal pyramid (emperor–shogun–daimyo–samurai–peasants) NEXT TO your Europe pyramid from Mission 8. Circle the matching levels.",
        "Bushido vs. jiu-jitsu: bushido valued discipline, respect, and self-control — write 3 sentences connecting it to your own martial arts training.",
     ],
     "cards": "\"1192 — first shogun appointed.\"",
     "check": "Side-by-side pyramids + the personal connection paragraph."},

    # ---- Unit 6 — West African Kingdoms (7.4) ----
    {"n": 17, "title": "Gold for Salt", "time": "40 min",
     "watch": "**Crash Course World History #16 \"Mansa Musa and Islam in Africa\"** (first half).",
     "steps": [
        "Learn: South of the Sahara, the empire of **Ghana** (then Mali, then Songhai) grew rich by taxing trade: **gold** from the south crossed the desert to meet **salt** from Saharan mines — salt was worth its weight in gold (needed to preserve food!).",
        "Trade game: chocolate chips = gold, salt packets = salt. Run 5 trades across a \"desert\" (the living room) with a caravan tax each crossing. Track who ends up rich — the kingdom in the middle!",
        "Map: label the Sahara, Niger River, Ghana/Mali region, Timbuktu.",
     ],
     "cards": "\"~800 — Ghana empire thrives.\"",
     "check": "She explains why the middleman kingdom got rich."},
    {"n": 18, "title": "Mansa Musa — Richest Man in History", "time": "40 min",
     "watch": "**Crash Course #16** (second half); search **\"Mansa Musa pilgrimage.\"**",
     "steps": [
        "Learn: Mali's king **Mansa Musa** may be the richest person who ever lived. His 1324 **hajj** (pilgrimage to Mecca) with tons of gold literally crashed gold prices in Egypt and put Mali on European maps.",
        "Primary source: find the Catalan Atlas image (1375) showing Mansa Musa holding a gold coin. Analyze: What does it show? Who made it? What does it prove about Mali's fame in Europe?",
        "Write a 5-sentence news report: \"Golden King Passes Through Cairo!\"",
     ],
     "cards": "\"1324 — Mansa Musa's hajj.\"",
     "check": "News report has 3+ accurate facts."},
    {"n": 19, "title": "Timbuktu & the Griots", "time": "40 min",
     "watch": "Search **\"Timbuktu manuscripts\"** images + **\"griot West Africa.\"**",
     "steps": [
        "Learn: **Timbuktu** became a world center of learning — its university and libraries held hundreds of thousands of manuscripts. History also lived in **griots**: trained oral historians who memorized centuries of family and kingdom history.",
        "Griot challenge: memorize and perform your own family's history going back as far as you can (grandparents minimum) as a 1-minute spoken performance — no notes.",
        "Compare knowledge-keeping across your course so far: monks copying (Europe), House of Wisdom (Islam), civil-service scholars (China), griots + Timbuktu (Africa). One sentence each.",
     ],
     "cards": "\"~1400s — Timbuktu's golden age.\"",
     "check": "Griot performance delivered; 4-way comparison done."},

    # ---- Unit 7 — The Americas: Maya, Aztec, Inca (7.7) ----
    {"n": 20, "title": "Maya — Masters of Time and Number", "time": "45 min",
     "watch": "Search **\"Crash Course Maya\"**; **Khan Academy \"Maya civilization.\"**",
     "steps": [
        "Learn: In Mesoamerican jungles, the **Maya** built city-states with pyramids, invented a written language, tracked planets with stunning accuracy, and used a math system with **zero** — base-20, written in dots (1) and bars (5).",
        "Maya math: learn the dot-bar system, then write today's date and your age in Maya numerals. Solve 3 addition problems entirely in Maya notation.",
        "Build a step pyramid from sugar cubes, LEGO, or cardboard layers.",
     ],
     "cards": "\"~600 CE — Maya golden age.\"",
     "check": "Maya numeral problems correct."},
    {"n": 21, "title": "Aztec — City on a Lake", "time": "40 min",
     "watch": "Search **\"Tenochtitlan\"** images and a short video.",
     "steps": [
        "Learn: The **Aztec** (Mexica) built **Tenochtitlán** on an island in a lake — canals for streets, causeways to shore, and floating farm-beds called **chinampas**. At ~200,000 people it rivaled any city in Europe. They ruled through the Triple Alliance and tribute from conquered peoples.",
        "Engineering build: make a floating garden — a foil or cork raft carrying a soil-and-seed bed that must float in a pan of water without sinking. Iterate until stable.",
        "City compare: Tenochtitlán vs. medieval Paris (~1400) — size, cleanliness (Aztecs bathed daily and had waste collection!), food supply. 3 sentences.",
     ],
     "cards": "\"1325 — Tenochtitlán founded.\"",
     "check": "Chinampa floats with load (photo)."},
    {"n": 22, "title": "Inca — Empire of the Andes", "time": "40 min",
     "watch": "Search **\"Inca empire roads quipu Machu Picchu\"** (short video + images).",
     "steps": [
        "Learn: The **Inca** ran a 2,500-mile mountain empire with **14,000+ miles of roads**, runner-messengers, **terrace farming** carved into slopes, and **quipu** — knotted cords that recorded numbers. All without wheels, iron, or writing.",
        "Make a quipu: hang 4 strings from a pencil. Encode your family's ages and this year using knot positions (ones/tens/hundreds levels). Have Dad \"read\" it with your key.",
        "Terrace demo: build 3 stepped dirt/dough terraces on a tilted tray; pour water at the top — watch terraces slow erosion vs. a plain slope.",
     ],
     "cards": "\"1438 — Inca empire expands.\"",
     "check": "Quipu decodes correctly."},

    # ---- Unit 8 — Renaissance & Reformation (7.8, 7.9) ----
    {"n": 23, "title": "Rebirth in Italy", "time": "45 min",
     "watch": "**Crash Course World History #22 \"The Renaissance\"**; **CKHG** Renaissance chapters.",
     "steps": [
        "Learn: ~1350–1550, Italian trade cities (Florence, Venice) grew rich; wealthy patrons like the **Medici** funded art and learning. **Humanism** = renewed focus on human achievement and classical Greek/Roman texts. Stars: **Leonardo da Vinci** (art + engineering), **Michelangelo** (David, Sistine Chapel).",
        "Perspective drawing: learn one-point perspective (vanishing point + guidelines) and draw a hallway or road receding into the distance — the Renaissance technique that made flat paintings look 3D.",
        "Da Vinci page: pick one of his inventions (flying machine, tank, parachute) and sketch it notebook-style with mirror-writing your name like he did.",
     ],
     "cards": "\"1503 — Mona Lisa painted.\"",
     "check": "Perspective drawing shows a vanishing point."},
    {"n": 24, "title": "The Machine That Changed Everything", "time": "45 min",
     "watch": "Search **\"Gutenberg printing press how it worked.\"**",
     "steps": [
        "Learn: ~1440, **Johannes Gutenberg** combined movable metal type + press = books went from months of hand-copying to hundreds of copies fast and cheap. Ideas could now spread faster than any king or church could stop them.",
        "Build a foam printing press: cut letters (BACKWARDS!) from craft foam, glue to cardboard blocks, ink with marker or paint, and print your name or a word 10 times. Feel the speed vs. hand-lettering your illuminated page in Mission 9.",
        "Chain reaction: write the chain — printing → cheap books → more readers → ideas spread → (this loads the next mission...).",
     ],
     "cards": "\"1440 — Gutenberg's press.\"",
     "check": "10 clean prints (photo)."},
    {"n": 25, "title": "Luther Lights the Fuse", "time": "40 min",
     "watch": "Search **\"Protestant Reformation explained\"**; **Khan Academy \"Reformation.\"**",
     "steps": [
        "Learn: In **1517**, monk **Martin Luther** posted his **95 Theses** protesting church corruption (especially selling **indulgences** — paying money for forgiveness). Thanks to the printing press, his ideas swept Europe in weeks. Result: **Protestant** churches split from Catholic; Europe divided.",
        "Make your own \"5 Theses\" poster: pick something you think should be fixed (in the world, school design, sports rules) and write 5 numbered arguments, nailed-to-the-door style.",
        "Connect: 2 sentences on why Luther succeeded where earlier protesters failed (hint: Mission 24).",
     ],
     "cards": "\"1517 — 95 Theses.\"",
     "check": "Poster + the printing-press connection."},
    {"n": 26, "title": "The Catholic Comeback & a Divided Europe", "time": "35 min",
     "watch": "**CKHG** Reformation chapters (Counter-Reformation section).",
     "steps": [
        "Learn: The Catholic Church answered with the **Counter-Reformation**: the Council of Trent fixed abuses, new orders like the **Jesuits** built schools and missions worldwide. But religious wars scarred Europe for a century.",
        "Map: shade a Europe map ~1600 — Protestant north (England, Scandinavia, N. Germany) vs. Catholic south (Spain, Italy, France) — and notice the pattern.",
        "Unit Big Idea paragraph (4 sentences): how did the Renaissance + printing press + Reformation together break the medieval world?",
     ],
     "cards": "\"1545 — Council of Trent.\"",
     "check": "Map pattern correct; paragraph links all three forces."},

    # ---- Unit 9 — Scientific Revolution (7.10) ----
    {"n": 27, "title": "The Universe Rearranged", "time": "40 min",
     "watch": "Search **\"Scientific Revolution Copernicus Galileo Newton for students.\"**",
     "steps": [
        "Learn the relay: **Copernicus** (1543 — Sun at the center, not Earth) → **Galileo** (telescope evidence; put on trial for it) → **Newton** (1687 — laws of motion and gravity explain it all with math).",
        "Galileo's experiment: he claimed heavy and light objects fall at the same speed. Test it — drop a big book and a single sheet of paper (crumpled tight) from the same height. Then uncrumpled. What role does air resistance play? Write your observation like a scientist: claim → evidence → conclusion.",
        "Why was heliocentrism dangerous to say out loud in 1600? 2 sentences.",
     ],
     "cards": "\"1543 — Copernicus publishes\" and \"1687 — Newton's Principia.\"",
     "check": "Claim-evidence-conclusion write-up."},
    {"n": 28, "title": "The Method Behind It All", "time": "35 min",
     "watch": "Search **\"scientific method steps.\"**",
     "steps": [
        "Learn: The real revolution was the **scientific method** — question → hypothesis → experiment → evidence → conclusion — trusting observation and testing over ancient authority.",
        "Run one full cycle on a question of your choice (Which paper airplane design flies farthest? Which room in the apartment is coldest?). Document every step on one page.",
        "Connect backward: which earlier civilizations in this course fed the Scientific Revolution? (Greek texts preserved by Muslims and monks, Arabic numbers and algebra, Chinese printing, universities.) List 3 threads.",
     ],
     "cards": "one card of your choice.",
     "check": "One-page method write-up with all 5 steps."},

    # ---- Unit 10 — Exploration & Enlightenment (7.11) ----
    {"n": 29, "title": "The Age of Exploration", "time": "45 min",
     "watch": "**Crash Course World History #21 \"Columbus, de Gama, and Zheng He\"**; **CKHG** exploration chapters.",
     "steps": [
        "Learn: New ships (caravels), the compass (thanks, China), and better maps let Europeans sail the open ocean seeking Asian spices: **Dias** (around Africa's tip 1488), **da Gama** (to India 1498), **Columbus** (to the Americas 1492 — by accident), **Magellan's** crew (around the world 1522).",
        "Yarn-map all four routes on your world map in different colors with a key.",
        "Motivation ranking: God, gold, glory — rank the \"3 G's\" for why explorers sailed and defend your order in 3 sentences.",
     ],
     "cards": "\"1492 — Columbus reaches the Americas.\"",
     "check": "Four routes mapped with key."},
    {"n": 30, "title": "The Columbian Exchange", "time": "45 min",
     "watch": "**Crash Course World History #23 \"The Columbian Exchange.\"**",
     "steps": [
        "Learn: Contact between hemispheres swapped everything: Americas → world (potatoes, corn, tomatoes, chocolate); world → Americas (horses, wheat, cattle — and devastating **diseases** like smallpox that killed most of the Native population; plus the tragedy of the Atlantic slave trade to work new plantations).",
        "Kitchen audit: check tonight's dinner ingredients — sort each as \"Old World\" or \"New World\" origin. (Pizza = wheat/cheese Old, tomato New!)",
        "Two-column impact chart: Gains vs. Terrible Costs of the Exchange, 3 items each. Historians hold both truths at once.",
     ],
     "cards": "\"1500s — Columbian Exchange transforms the world.\"",
     "check": "Dinner sort + balanced impact chart."},
    {"n": 31, "title": "The Enlightenment — Ideas That Built America", "time": "40 min",
     "watch": "**Khan Academy / Crash Course \"The Enlightenment.\"**",
     "steps": [
        "Learn the thinkers: **Locke** (natural rights — life, liberty, property; government by consent), **Montesquieu** (separation of powers — three branches!), **Rousseau** (the social contract), **Voltaire** (free speech, religious tolerance).",
        "Matching proof: print or copy 3 short lines from the **Declaration of Independence** and **U.S. Constitution**; draw arrows matching each to the thinker whose idea it echoes.",
        "Complete the course-long chain: Magna Carta (1215) → English Bill of Rights (1689) → Enlightenment → Declaration of Independence (1776). One sentence per link.",
     ],
     "cards": "\"1689 — English Bill of Rights\" and \"1776 — Declaration of Independence.\"",
     "check": "Arrows match ideas to thinkers correctly."},
    {"n": 32, "title": "Capstone — Museum of a Thousand Years", "time": "60 min",
     "watch": "Nothing — today you walk the whole timeline.",
     "steps": [
        "Your wall timeline now spans 300–1789 with 20+ event cards. Review it start to finish.",
        "Write the course essay (one page, 3 paragraphs): **\"How did the world of 1789 become so different from the world of 300 CE?\"** Use at least 5 specific events/people from your timeline. Structure: (1) the old world fragments and reorganizes, (2) trade and ideas connect the continents, (3) printing + science + Enlightenment create the modern world.",
        "Give Dad and Violet a 10-minute timeline tour: walk the wall, tell the story, show your 3 favorite builds (compass? printing press? quipu?).",
     ],
     "cards": "review your whole 300–1789 timeline (20+ cards) — no new card.",
     "check": "Essay cites 5+ specifics; tour delivered. COURSE COMPLETE — file the essay + timeline photo in the PSA course-of-study record."},
]

UNIT_OF = {
    **{n: "Unit 1 · Rome & Byzantium" for n in range(1, 4)},
    **{n: "Unit 2 · The World of Islam" for n in range(4, 8)},
    **{n: "Unit 3 · Medieval Europe" for n in range(8, 12)},
    **{n: "Unit 4 · Imperial China" for n in range(12, 15)},
    **{n: "Unit 5 · Medieval Japan" for n in range(15, 17)},
    **{n: "Unit 6 · West Africa" for n in range(17, 20)},
    **{n: "Unit 7 · The Americas" for n in range(20, 23)},
    **{n: "Unit 8 · Renaissance & Reformation" for n in range(23, 27)},
    **{n: "Unit 9 · Scientific Revolution" for n in range(27, 29)},
    **{n: "Unit 10 · Exploration & Enlightenment" for n in range(29, 33)},
}


def mission_blocks(m):
    """Build Kaylin's uniform mission Material (with the timeline-card completion)."""
    return [
        (LessonBlock.KIND_MASTHEAD, {
            "eyebrow": f"World History · {UNIT_OF[m['n']]} · Mission {m['n']}",
            "title": m["title"],
            "thesis": f"About {m['time']}. Read it, do it, add to your timeline, show what you know.",
        }),
        (LessonBlock.KIND_PURPOSE, {
            "title": "Read / Watch first",
            "paragraphs": [m["watch"]],
        }),
        (LessonBlock.KIND_STEPS, {
            "title": "Do this",
            "steps": [{"detail": s} for s in m["steps"]],
        }),
        (LessonBlock.KIND_RECAP, {
            "title": "Show what you know",
            "items": [
                f"**Add to your wall timeline:** {m['cards']}",
                "Open your **History Log** below 👇 and write your **Big Idea** + **3 facts**.",
                "**Turn it in** so Dad can review it and stamp the mission complete.",
                "**Snap a photo** of your timeline or build for your Work Log.",
            ],
        }),
    ]


class Command(BaseCommand):
    help = "Seed Kaylin's Grade 7 World History mission course (idempotent, no AI)."

    def add_arguments(self, parser):
        parser.add_argument("--child-name", default="Kaylin",
                            help="Child first name to build the course for.")

    def handle(self, *args, **options):
        name = options["child_name"]
        child = Student.objects.filter(first_name__iexact=name).order_by("pk").first()
        if child is None:
            raise CommandError(f"No student named {name!r} found.")

        curriculum, made = Curriculum.objects.get_or_create(
            parent=child.parent,
            name=WORLD_HISTORY_G7["name"],
            defaults={
                "family": child.family,
                "subject": WORLD_HISTORY_G7["subject"],
                "grade_level": WORLD_HISTORY_G7["grade_level"],
            },
        )
        self.stdout.write(("Created" if made else "Found") + f" curriculum #{curriculum.pk} '{curriculum.name}'.")

        apply_blueprint(curriculum, WORLD_HISTORY_G7)
        CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum, defaults={"is_active": True})

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
            for order, (kind, data) in enumerate(blocks, start=1):
                LessonBlock.objects.update_or_create(
                    material=material, order=order, defaults={"kind": kind, "data": data})
            LessonBlock.objects.filter(material=material, order__gt=len(blocks)).delete()
            add_journal(
                curriculum, child, m["n"],
                title=f"Mission {m['n']} · History Log",
                intro=JOURNAL_INTRO,
                questions=journal_questions(m),
                quiz=mission_quiz("ss_kaylin", m["n"]),
            )
            seeded += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {seeded} missions + History Logs (APPROVED) for {child.first_name} "
            f"— curriculum #{curriculum.pk}. Turning in the log fires AI encouragement + "
            f"a draft for you to stamp."
        ))
