"""The Year of Miss Agnes (Kirkpatrick Hill) — Blackbird & Company guide.

The family's purchased Literature Discovery Guide, digitised for private use.
Same product line and level as the Rickshaw Girl guide already in the app, and
the same five-part shape:

    Read       the section's chapters
    Journal    Characters · Setting · Plot
    Acquire    vocabulary — match the definitions, then fill the blanks
    Recollect  comprehension questions, answered in complete sentences
    Explore    a paragraph (rough draft → final draft) + discussion questions
    Glean      section 5: a final project, chosen from the guide's options

Differences from the Rickshaw Girl guide, following the book:
  - reading splits are Chapters 1-4 / 5-9 / 10-13 / 14-17
  - each Journal page names TWO characters, not four
  - the Glean page misnumbers its options 1, 2, 3, 3, 4, 5 — six options in
    all, two of them printed as "3."; the pairs below keep the printed order

`answers` on each vocabulary entry is the guide's key: the definition number
for the matching exercise. `blanks` are the fill-in sentences with ___ where
the word goes, paired with the word that belongs there — every answer in this
guide fits in its listed form (no inflections needed, unlike Rickshaw §4).

Transcribed by reading the rendered pages, not the PDF text layer, which
mangles exactly the words a child would copy (it prints "Bakko" for "Bokko"
on three pages where the ink clearly reads "Bokko").
"""

# Must match the blueprint entry — the seed creates the curriculum from it.
CURRICULUM_NAME = "The Year of Miss Agnes — Literature Discovery"
BOOK = "The Year of Miss Agnes by Kirkpatrick Hill"

# The guide's own framing, from its introduction.
HOW_IT_RUNS = (
    "The guide is designed to be completed in five weeks. The reading and the "
    "core of the guide should be completed in four, with the fifth week devoted "
    "to the final project or assignment."
)

JOURNAL_NOTE = (
    "Notes should be recorded in the form of bullet point phrases. Character "
    "notes should be about WHO a character is, not what he does — what a "
    "character does is plot information."
)

SECTIONS = [
    {
        "number": 1,
        "chapters": "Chapters 1–4",
        "characters": ["Mamma", "Fred"],
        "definitions": [
            "an annoying person or thing",
            "to move while shaking",
            "a device used for catching animals",
            "shoes made of soft leather",
            "a large feather from a bird",
            "straps that form the gear of a working animal",
        ],
        # word -> the number of its definition above, in the guide's own order
        "vocab": [("harness", 6), ("trap", 3), ("quill", 5),
                  ("nuisance", 1), ("waggle", 2), ("moccasins", 4)],
        "blanks": [
            ("Jordan watched the leaves in the trees ___ as the strong wind "
             "blew.", "waggle"),
            ("On cold nights I like to wear my ___ around the house.",
             "moccasins"),
            ("The husky had to wear a ___ in order to pull the sled.",
             "harness"),
            ("In colonial times writing would be done with a ___ because pens "
             "had not been invented.", "quill"),
            ("The crying child was a ___ during the movie.", "nuisance"),
            ("We have to set out a ___ every night in order to catch the "
             "mouse.", "trap"),
        ],
        "comprehension": [
            "What does Sam tell Fred he brought for her on October 1, 1948?",
            "What have Fred and Bertha never seen?",
            "Who is Fred named after?",
            "Why does the village need to have a school?",
            "Why doesn't Bokko go to school?",
            "What does Mamma think everyone should be doing instead of going "
            "to school?",
            "Why does Fred's grandma grumble at Mamma?",
        ],
        "writing_prompt": (
            "Write a paragraph describing something you would like to learn "
            "about. Describe what it is and how you might be able to learn it."
        ),
        "discussion": [
            "What types of things does Fred think the old teacher will tell "
            "Sam? Why do you think the teacher might have these complaints? "
            "Do you ever complain? Why? How does complaining make you feel?",
            "Why do you think Bertha doesn't try the milk in her tea when "
            "Miss Agnes offers her some? Have you ever refused to try "
            "something new? Why or why not? Give an example.",
            "Why does Fred think Roger is a nuisance? Have you ever been "
            "around someone who is a nuisance? Have you ever been a nuisance? "
            "Give an example.",
            "When Fred goes to school the first day with Miss Agnes as her "
            "teacher, what is different? Why?",
            # The guide prints "items is your home" — its own typo for "in".
            "What types of things, according to Fred's grandma, used to be "
            "made by hand? What skills did Fred and her sister learn from "
            "their grandmother? What skills have you learned from your "
            "family? Are there any handmade items is your home?",
        ],
    },
    {
        "number": 2,
        "chapters": "Chapters 5–9",
        "characters": ["Bokko", "Mamma"],
        "definitions": [
            "difficult to please",
            "to shout",
            "the study of the earth's surface",
            "to make someone self-conscious",
            "to squat down close to the ground",
            "basic mathematics",
        ],
        "vocab": [("holler", 2), ("arithmetic", 6), ("hunker", 5),
                  ("picky", 1), ("geography", 3), ("embarrass", 4)],
        "blanks": [
            ("Jill would ___ her friend by tripping her during dance "
             "practice.", "embarrass"),
            ("Taylor would often ___ down in the living room to build with "
             "blocks.", "hunker"),
            ("Mother had to ___ so that her toddler would not run into the "
             "street in front of the bus.", "holler"),
            ("The 3rd grade teacher tested her students on their ___ every "
             "Wednesday morning.", "arithmetic"),
            ("The boy was a ___ eater and would not taste the tuna sandwich.",
             "picky"),
            ("While studying ___, the class learned about the many mountain "
             "ranges in the United States.", "geography"),
        ],
        "comprehension": [
            "How does Miss Agnes get Little Pete and Roger to stop wrestling?",
            "Why does Miss Agnes put the ugly old grade book into a cardboard "
            "box to be stored in the cache?",
            "Why does Fred make a picture of Miss Agnes?",
            "What does Miss Agnes tell Bertha she is ready to learn?",
            "Why does Miss Agnes want the children to learn arithmetic?",
            "What does Miss Agnes order from Sam White to help Bokko learn?",
            "How do Fred and Bokko know that their mother isn't mad at Miss "
            "Agnes anymore?",
        ],
        "writing_prompt": (
            "Write a paragraph about a place in the world you would like to "
            "go and why. Look at a map or an atlas to get some ideas."
        ),
        "discussion": [
            "What does Miss Agnes ask her students to draw on her first day "
            "of teaching? Why do you think the first thing Miss Agnes "
            "assigned her new students was to make a picture for the school "
            "wall? Do you think this was an important assignment? Why or why "
            "not?",
            "Why does Bertha like to copy writing printed on boxes even "
            "though she doesn't know what the letters mean? Do you agree "
            "with her? Why or why not?",
            "Why does Miss Agnes tell her students that if their letters are "
            "sloppy she will make them do their work over? How does this "
            "make Fred feel? Why do you think she feels this way? What do "
            "you think about this policy?",
            # "Robin Hood" is italicised in print.
            "Why do you think Fred doesn't want Miss Agnes to stop reading "
            "Robin Hood? Do you prefer listening to stories or reading "
            "stories? Why?",
            "What was Miss Agnes going to teach her students about "
            "geography? Why do you think she wants her students to know this "
            "information? How does Fred feel about learning geography? Why "
            "do you think she feels this way?",
            "Fred thinks there is no way that Miss Agnes could make "
            "arithmetic fun. How does Miss Agnes make Fred decide to get "
            "better at arithmetic? Why do you think arithmetic is important?",
            "Do you think Fred's mother is more angry or scared about Bokko "
            "attending school? Why? Why do you think she let her go in the "
            "end?",
            "Why do you think Miss Agnes believes school is not just for "
            "kids? Do you agree? Why or why not?",
        ],
    },
    {
        "number": 3,
        "chapters": "Chapters 10–13",
        "characters": ["Fred", "Miss Agnes"],
        "definitions": [
            "an instrument used to see very small particles",
            "a group of people with the same interests or culture",
            "an old-fashioned record player",
            "easily broken",
            "to catch",
            "a sound heard again after being reflected",
        ],
        "vocab": [("community", 2), ("brittle", 4), ("snare", 5),
                  ("microscope", 1), ("echo", 6), ("phonograph", 3)],
        "blanks": [
            ("In science class, Henry was fascinated by what he could see in "
             "a drop of water while looking at it under the ___.",
             "microscope"),
            ("The sly fox was always trying to ___ Little Red Riding Hood.",
             "snare"),
            ("My grandmother loves to play jazz records on her old ___.",
             "phonograph"),
            ("Little Italy is a ___ in New York where many Italians live.",
             "community"),
            ("I could hear an ___ when I clapped my hands loudly in the "
             "empty hallway.", "echo"),
            ("After the storm, there was a ___ layer of ice on the lake.",
             "brittle"),
        ],
        "comprehension": [
            "When does Miss Agnes take her squeeze box out of its little "
            "case?",
            "What happens if the dance in the community hall goes on long "
            "enough?",
            "What does Miss Agnes make with skinny white paper from "
            "Anderson's adding machine?",
            "Why don't Fred's grandfather and his friends know about World "
            "War I?",
            "What does Fred think about looking into the microscope?",
            "What made Miss Agnes homesick?",
            "What does Fred's grandfather say happened when the priest "
            "photographed the people of the village?",
        ],
        "writing_prompt": (
            "Ask a family member to tell you a story from their childhood "
            "and then write a paragraph about it."
        ),
        "discussion": [
            "Why do you think Miss Agnes doesn't dance at the gathering in "
            "the community hall when everyone else is dancing?",
            "Why do you think Fred and her classmates like to play “time "
            "machine” with Miss Agnes?",
            # The guide prints "friend's" — its own apostrophe for "friends".
            "Why do you think Fred and her friend's like to sit around and "
            "listen to her grandfather and his friends talk about the old "
            "times? Have you ever listened to a grandparent telling a story "
            "from the past?",
            # The quoted sentence is italicised in print.
            "Fred says that, “With Miss Agnes the world got bigger and then "
            "it got smaller.” What do you think she means? Do you agree or "
            "disagree? Why?",
            "Why do you think Fred and her classmates think people from the "
            "village can't go to college? How does Miss Agnes change their "
            "minds?",
            "What thoughts does Fred have when she sees the photograph of "
            "herself? What do you think when you see a photograph of "
            "yourself? Are your thoughts similar or different than Fred's "
            "thoughts?",
        ],
    },
    {
        "number": 4,
        "chapters": "Chapters 14–17",
        "characters": ["Fred", "Miss Agnes"],
        "definitions": [
            "dark or dim",
            "to create something new",
            "to speak highly of oneself",
            "a state or nation",
            "to be unable to remember",
            "a person ordained as a minister",
        ],
        "vocab": [("brag", 3), ("forget", 5), ("invent", 2),
                  ("gloomy", 1), ("priest", 6), ("country", 4)],
        "blanks": [
            ("When my uncle got married, a ___ performed the wedding.",
             "priest"),
            ("John tried to ___ a machine that would wash his dog.",
             "invent"),
            ("It's not considered polite to ___, even if you do have the "
             "highest score.", "brag"),
            ("Mother told me many times not to ___ to brush my teeth before "
             "going to bed.", "forget"),
            ("The stormy weather made the sky look ___.", "gloomy"),
            ("Brazil is a ___ in South America.", "country"),
        ],
        "comprehension": [
            "What does Miss Agnes have her students read instead of the "
            "books about Dick and Jane?",
            "Why does Miss Agnes give each of her students little notebooks?",
            "Why does Fred think that good English sounds wrong?",
            "What does Miss Agnes leave behind when she packs her things?",
            # Printed as "5.What job..." — no space after the number.
            "What job do Fred and her sister Bokko have at fish camp?",
            "What happens when Fred thinks about the things Miss Agnes "
            "taught her?",
            "What do Fred and Bokko discover when they return from fish "
            "camp?",
        ],
        "writing_prompt": (
            "Miss Agnes encouraged her students to make up pretend stories. "
            "Make up a short pretend story of your own."
        ),
        "discussion": [
            "What does Fred think of the books about Dick and Jane? What "
            "does she think of the books Miss Agnes made for her to read? "
            "Which do you think she prefers? Why?",
            "Miss Agnes tells her students that writing is reading "
            "backwards. What do you think she means by this?",
            "Miss Agnes tells her students that everyone is good at "
            "something. What are you good at?",
            "Miss Agnes tells her students that there are lots of right "
            "ways to talk. Do you think she says that to make her students "
            "feel good or do you think Miss Agnes really believes it? What "
            "do you think?",
            "What changes in Fred's mother do you notice at the end of the "
            "book? Why do you think she changed?",
        ],
    },
]

# Section 5 — the guide's own list, each paired with a short name so a child
# can scan the options instead of reading a page of prose. The printed page
# numbers its six options 1, 2, 3, 3, 4, 5 (two "3."s) — kept in that order.
FINAL_PROJECT_INTRO = "Complete one or more of the following assignments."
FINAL_PROJECT_OPTIONS = [
    ('Alaska state report',
     'Do some research and write a state report about Alaska. Make a map using art supplies.'),
    ('England country report',
     'Do some research and write a country report about England. Make a map using art supplies.'),
    # Printed "3." — the first of the two options the guide numbers 3.
    ('World map of your places',
     'Draw a map of the world. Locate and label important places that relate to you and your family. For example, where you were born, places you have visited, where your grandparents are from, etc.'),
    # Also printed "3." — the guide's own misnumbering, kept in printed order.
    ('Paper time line of your life',
     'Make a paper time line about your life. Include major information not only about yourself but about your country and your world.'),
    # The opening sentence of the story is italicised in print.
    ('Paper book about yourself',
     'Construct a small paper book and write a story about yourself. Start your story by saying, “There was once a little girl (or boy) named _____________.”'),
    ('Pretend to be Miss Agnes',
     'Pretend you are Miss Agnes. Write a paragraph explaining to Fred and Bokko why you decided to return to the village.'),
]


def section_by_number(number):
    return next((s for s in SECTIONS if s["number"] == number), None)


def matching_key(section):
    """The guide's answer key for the matching exercise: word -> definition no."""
    return {word: n for word, n in section["vocab"]}
