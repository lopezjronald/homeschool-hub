"""Studies Weekly Level 7, Week 1 — Geography and Map Skills.

California Studies Weekly: World History and Geography, Medieval and Early
Modern Times. Unit 1, Lesson 1.1. Kaylin's.

Transcribed from the family's issue. The questions and their options are the
printed wording; the answers are the teacher edition's own marked answers
(pp. 1.13-1.14), and `standard` on each question is that edition's Assessment
Map — which framework strand it assesses — so the record can show a reviewing
teacher what each question was for.

The figures are cropped from the issue at 4x. Several questions say "study the
map" and mean one specific map: the biome map's answer is read off its scale
bar, and the grid map's answer depends on where California sits on it. A
substitute map would make those questions unanswerable.

Digitized from the family's purchased Studies Weekly issue for private use.
"""

from .weekly import choice, fill_two, matching, written, figure, page_images

LEVEL = 7
WEEK = 1
UNIT = 1
LESSON = "1.1"
TITLE = "Geography and Map Skills"
SUBTITLE = "Where in the World? Geography Basics"
ESSENTIAL_QUESTION = "How do we know what happened in the past?"
PUBLICATION = "California Studies Weekly: Medieval and Early Modern Times"

# The two article pages of the issue, as scans. The layout IS the lesson here —
# a newspaper spread with the world map, the five themes in tinted boxes and the
# vocabulary running down the side — and retyping it as prose would throw that
# away for no gain.
PAGES = page_images(LEVEL, WEEK, 2)

# The issue's own vocabulary sidebar, verbatim.
VOCABULARY = [
    ("cardinal directions", "four directions on a compass: north, south, east, and west"),
    ("cartographer", "a person who creates maps"),
    ("compass rose", "a map symbol showing cardinal directions"),
    ("Equator", "an imaginary line dividing the Earth into the Northern and "
                "Southern hemispheres"),
    ("geography", "the study of the relationships between Earth's landscapes, the "
                  "atmosphere, bodies of water, and the societies that inhabit it"),
    ("human geography", "the study of how humans adapt to natural geographic "
                        "environments"),
    ("human migration", "the movement of people from one place to another"),
    ("hemispheres", "imaginary lines that divide the Earth into four sections: "
                    "Northern, Southern, Eastern, and Western"),
    ("International Date Line (IDL)", "an imaginary line between the North Pole and "
                                      "South Pole that defines time between days"),
    ("latitude", "the imaginary horizontal lines that measure how far north or south "
                 "places are from the Equator"),
    ("legend", "explains what the symbols and colors mean on a map"),
    ("longitude", "imaginary vertical lines from the North Pole to the South Pole "
                  "that indicate distance from the Prime Meridian"),
    ("physical geography", "the study of the exterior physical features and changes "
                           "of the Earth"),
    ("Prime Meridian", "an imaginary line dividing the world into the Eastern and "
                       "Western hemispheres"),
    ("scale", "a measurement key for distance on a map"),
]

# The five themes, from the article's tinted box — the source for question 2.
THEMES = [
    ("Location", "Understanding where things are on Earth's surface is fundamental "
                 "to geography."),
    ("Place", "This theme explores the unique characteristics and features defining "
              "specific locations."),
    ("Human-Environment Interaction", "Geographers study how human activities impact "
                                      "the environment and vice versa."),
    ("Movement", "The movement of people, goods, ideas, and information across the "
                 "globe is a crucial aspect of geography."),
    ("Region", "Regions with shared characteristics help us grasp the world's "
               "diversity."),
]

F = lambda name: figure(LEVEL, WEEK, name)          # noqa: E731 — reads better here

# The teacher edition's Assessment Map, as a short label per question.
HSS = "History–Social Science Framework: Global Convergence, 1450–1750"
C3_D2 = "C3 Framework, Dimension 2: Applying Disciplinary Concepts and Tools"
C3_D3 = "C3 Framework, Dimension 3: Evaluating Sources and Using Evidence"

QUESTIONS = [
    fill_two(
        "___A___ and ___B___ are the two branches of geography.",
        bank_a=["Physical geography", "Human geography", "Location geography",
                "Region geography"],
        bank_b=["physical geography", "human geography", "location geography",
                "region geography"],
        correct_a="Physical geography",
        correct_b="human geography",
        hint="The article names them in its first paragraph, right before it "
             "explains each one.",
        standard=HSS,
    ),
    matching(
        "Match each question to the theme that answers it.",
        pairs=[
            ('"How and why are places connected?"', "movement"),
            ('"What is it like there?"', "place"),
            ('"Why is California different from Nevada?"', "region"),
            ('"Where is San Francisco?"', "location"),
            ('"Why is it harder to travel through mountains?"',
             "human-environment interaction"),
        ],
        hint="All five themes are in the tinted box on the first page of the "
             "article.",
        standard="%s · %s" % (HSS, C3_D2),
    ),
    choice(
        "Which example is a human-environment interaction?",
        options=[
            ("a", "José Barreiro writing about the Taíno."),
            ("b", "A hurricane forming in the Atlantic Ocean."),
            ("c", "Engineers constructing the Hoover Dam."),
            ("d", "Spanish explorers discovering the New World."),
        ],
        correct="c",
        hint="Human-environment interaction needs BOTH a person doing something "
             "and the environment changing because of it.",
        standard=HSS,
    ),
    choice(
        "Which are examples of human geography?",
        options=[
            ("a", "", F("q4a-cornfield")),
            ("b", "", F("q4b-house")),
            ("c", "", F("q4c-mountain")),
            ("d", "", F("q4d-coast")),
            ("e", "", F("q4e-terraces")),
        ],
        correct=["a", "b", "e"],
        multi=True,
        hint="Human geography is about how people change or use the land. Ask of "
             "each picture: did somebody make this, or was it already there?",
        standard="%s · %s" % (HSS, C3_D2),
    ),
    choice(
        "Study the image. Kevin is using source A. What is Kevin doing?",
        options=[
            ("a", "communicating with friends"),
            ("b", "finishing a math assignment"),
            ("c", "ordering goods and services"),
            ("d", "moving between two locations"),
        ],
        correct="d",
        figure=F("q5-source-a"),
        figure_caption="Source A",
        hint="Look at what is actually on the screens — the red line is doing "
             "the telling.",
        standard="%s · %s" % (HSS, C3_D3),
    ),
    choice(
        "Study the map. What is the largest east-west distance in miles of the "
        "Eastern biome? Use the map scale and do not cross over water. Write "
        "your answer as a whole number.",
        options=[("a", "500"), ("b", "1,000"), ("c", "2,200"), ("d", "6,000")],
        correct="c",
        figure=F("q6-biomes"),
        figure_caption="Biomes of North America",
        hint="Find the Eastern biome in the legend first, then measure its widest "
             "part against the scale of miles.",
        standard="%s · %s" % (HSS, C3_D3),
    ),
    choice(
        "Which line divides the Earth into Western and Eastern Hemispheres?",
        options=[
            ("a", "Equator"),
            ("b", "Prime Meridian"),
            ("c", "Greenwich Mean Line"),
            ("d", "International Date Line"),
        ],
        correct="b",
        hint="The Equator runs the other way — it divides north from south. This "
             "one is in your vocabulary list.",
        standard=HSS,
    ),
    choice(
        "Study the map. Which statement is not true?",
        options=[
            ("a", "California is in North America."),
            ("b", "California is in the United States."),
            ("c", "California is in the Southern Region."),
            ("d", "California is in the Western Hemisphere."),
        ],
        correct="c",
        figure=F("q8-grid-world"),
        figure_caption="World map with hemispheres and a coordinate grid",
        hint="Careful — this one asks which is NOT true. Find California on the "
             "map, then check each statement against it.",
        standard="%s · %s" % (HSS, C3_D3),
    ),
    fill_two(
        "Study the map, then choose the word that best completes the sentence: "
        "The United States is ___A___ of the Equator and lies ___B___ of Africa.",
        bank_a=["north", "east", "west", "south"],
        bank_b=["west", "east", "north", "south"],
        correct_a="north",
        correct_b="west",
        figure=F("q9-physical-map"),
        figure_caption="Physical Map of the World",
        hint="The red line is the Equator and the blue one is the Prime Meridian "
             "— the legend says so.",
        standard="%s · %s" % (HSS, C3_D3),
    ),
    choice(
        "Which is most closely related to the International Date Line?",
        options=[
            ("a", "time zones"),
            ("b", "lines of latitude"),
            ("c", "climate regions"),
            ("d", "coordinate grid"),
        ],
        correct="a",
        hint="Your vocabulary list says the IDL \"defines time between days\". "
             "Which of these is about time?",
        standard=HSS,
    ),
]

# One open question of our own, after the check: the issue's Essential Question,
# asked of her in writing. The printed check is all recall and reading; this is
# where she says something. It carries the answer-mode picker.
REFLECTION = written(
    "This unit's big question is: **How do we know what happened in the past?** "
    "Geographers read maps for evidence. Using the maps in this issue, write "
    "three or four sentences about something a map can tell you that words "
    "alone could not.",
    hint="Think about the biome map — could you have described where the Eastern "
         "biome ends, in words, as quickly as the map showed you?",
    standard="%s · %s" % (HSS, C3_D3),
)
