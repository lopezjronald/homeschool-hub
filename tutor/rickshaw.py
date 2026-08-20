"""Rickshaw Girl (Mitali Perkins) — Blackbird & Company Level 3 guide, for Violet.

The family's purchased Level 3 Literature Discovery Guide, digitised for private
use. Same product line as the Level 7 "I Am David" guide already in the app, and
the same five-part shape:

    Read       the section's chapters
    Journal    Characters · Setting · Plot
    Acquire    vocabulary — match the definitions, then fill the blanks
    Recollect  comprehension questions, answered in complete sentences
    Explore    a paragraph (rough draft → final draft) + discussion questions
    Glean      section 5: a final project, chosen from the guide's options

Level 3 differs from Level 7 in how vocabulary works: the child MATCHES words to
numbered definitions and fills in blanks, rather than looking words up and
writing her own sentences. Both exercise types already exist in the app, so the
portal keeps the guide's own format.

`answers` on each vocabulary entry is the guide's key: the definition number for
the matching exercise. `blanks` are the fill-in sentences with ___ where the word
goes, paired with the word that belongs there — note that two of section 4's want
an inflected form, which the key records as printed.

Transcribed by reading the rendered pages; the vocabulary pages especially, since
the PDF's text layer mangles them ("W h e n Jamie saw the rattlesnake").
"""

# Must match the blueprint entry — the seed creates the curriculum from it.
CURRICULUM_NAME = "Rickshaw Girl — Literature Discovery"
BOOK = "Rickshaw Girl by Mitali Perkins"

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
        "chapters": "Chapters 1–3",
        "characters": ["Naima", "Rashida", "Father", "Saleem"],
        "definitions": [
            "a small, roughly made shelter",
            "the sill of a door",
            "a small, two-wheeled vehicle pulled by a person on foot or on a bicycle",
            "a brief period of excitement or activity",
            "dirt that covers a surface",
            "creamy, off-white color",
        ],
        # word -> the number of its definition above
        "vocab": [("flurry", 4), ("grime", 5), ("hut", 1),
                  ("ivory", 6), ("rickshaw", 3), ("threshold", 2)],
        "blanks": [
            ("On our trip to India last summer, we toured part of the city on a ___.",
             "rickshaw"),
            ("The ___ on the kitchen sink needed to be scrubbed clean with bleach.",
             "grime"),
            ("Paige wore her vintage ___ dress to the piano recital.", "ivory"),
            ("Lila asked to peek inside the mud ___ to see how all the family "
             "members lived in such close quarters.", "hut"),
            ("Eddie enjoyed watching a ___ of snowflakes rush past his bedroom "
             "window.", "flurry"),
            ("The groom carried his bride across the ___ of their new house.",
             "threshold"),
        ],
        "comprehension": [
            "Even though most homes in the village look the same, how are they "
            "different during the holidays?",
            "What is International Mother Language Day, and what happens to the "
            "girl who paints the best alpanas?",
            "Why did Naima stop going to school after only three years?",
            "What does Naima compare wearing a saree too?",
            "Why does Naima's father have to work from dawn until midnight?",
            "In Bangladeshi culture, what does Naima say only girls are allowed "
            "to do?",
            "Why does Naima begin to wish she had been born a boy?",
        ],
        "writing_prompt": (
            "In Naima's village, people paint alpanas on holidays to celebrate "
            "their Bangladeshi culture. Write about a holiday or event in which "
            "you celebrate your religion or culture. What activities or "
            "traditions do you take part in?"
        ),
        "discussion": [
            "In Naima's village, people celebrate their Bangladeshi culture on "
            "International Mother Language Day. How do you celebrate your culture?",
            "Why isn't Naima allowed to talk to Saleem anymore? Do you think it "
            "is fair they aren't allowed to be friends?",
            "Even though Naima wanted to keep going to school, she had to stop "
            "because her family couldn't afford it. Have you ever been excluded "
            "from participating in something simply because it cost too much for "
            "your family?",
            "Rashida will have to leave school soon if they don't pay off the "
            "rickshaw loan, even though she is the best student at school. Do you "
            "think it is fair that in some places going to school is a luxury and "
            "not a right? How would you feel if you had to stop going to school "
            "in order to help support your family?",
        ],
    },
    {
        "number": 2,
        "chapters": "Chapters 4–6",
        "characters": ["Naima", "Saleem", "Mother", "Father"],
        "definitions": [
            "a series of wound circles, like in a spring",
            "to know and remember someone or something",
            "to change the usual appearance of someone or something",
            "a type of flowering plant that grows on the surface of water",
            "done, made, or said without being careful",
            "lacking genuine levity, mirthless",
        ],
        "vocab": [("careless", 5), ("coiled", 1), ("disguise", 3),
                  ("grim", 6), ("lotus", 4), ("recognize", 2)],
        "blanks": [
            ("When Jamie saw the rattlesnake ___ near the bush, she remembered to "
             "stay still and wait for it to slither away.", "coiled"),
            ("After Katie got her braces off, I almost didn't ___ her with that "
             "new smile.", "recognize"),
            ("When Finn put on his Hulk costume, he decided to talk in a deeper "
             "voice in order to ___ his true identity.", "disguise"),
            ("Olivia realized she had been ___ with her words, when she jokingly "
             "called her sister a smelly dog.", "careless"),
            ("The ___ flower glowed in the moonlight.", "lotus"),
            ("Justine made a ___ face after swallowing a mouthful of sour milk.",
             "grim"),
        ],
        "comprehension": [
            "What is Naima's big idea for helping her family?",
            "Why doesn't Saleem think Naima's idea will work?",
            "What does Naima picture in her mind's eye as she turns the pedals of "
            "the rickshaw?",
            "What happens to the rickshaw after Naima jumps off?",
            "What is the first thing Naima's mother asks after the crash?",
            "Why is Naima's father relieved?",
            "What does Naima's mother offer to trade for money?",
        ],
        "writing_prompt": (
            "Naima's accident may end up costing her family their future. Write "
            "about a time when you made a mistake that affected others. What "
            "happened? How did you feel? How was the situation resolved?"
        ),
        "discussion": [
            "Why does Saleem say Naima has a bad history with big ideas? Do you "
            "think she should have listened to Saleem? Have you ever had an idea "
            "that sounded good at first, but then turned out badly?",
            "Why does Naima decide to drive the rickshaw without asking for "
            "permission first? Do you think things would have turned out "
            "differently if she had talked to her parents before driving the "
            "rickshaw? Why do you think she didn't ask for help, even though she "
            "was trying something new for the first time and knew it could be "
            "dangerous?",
            "Why does Naima head straight to her mat after the crash?",
            "Why does Naima's mother offer to sell one of her bangles? Why are "
            "the bangles important to her and Naima's family? What does Naima's "
            "mother's sacrifice say about her values? Have you ever had to give "
            "up something that was precious to you?",
            "Why do you think Naima's mother sang her a lullaby?",
            "How do you think Naima felt when her father placed his palm on her "
            "head before leaving the hut? Can you describe a time when someone "
            "treated you kindly after you made a mistake?",
            "Have you ever treated someone kindly after they made a mistake? How "
            "did your actions affect the other person?",
        ],
    },
    {
        "number": 3,
        "chapters": "Chapters 7–10",
        "characters": ["Naima", "Saleem", "Mother", "Father"],
        "definitions": [
            "to spend time doing nothing",
            "the condition of feeling ashamed or becoming unworthy of respect",
            "unable to feel anything",
            "very small in amount or number",
            "having two sides or halves that are the same",
            "not bright or distinct",
        ],
        "vocab": [("dim", 6), ("disgrace", 2), ("idle", 1),
                  ("numb", 3), ("scarce", 4), ("symmetry", 5)],
        "blanks": [
            ("There is hardly a Saturday or Sunday where I have time to sit "
             "around and be ___.", "idle"),
            ("Laura felt ___ when her father caught her lying about getting her "
             "homework finished before she played outside.", "disgrace"),
            ("It is fun to look in the mirror and see the ___ of my facial "
             "features.", "symmetry"),
            ("After being bitten by the vicious dog, Jay felt ___ and couldn't "
             "talk about it for a few days.", "numb"),
            ("The fish in the shallow pond were quite ___.", "scarce"),
            ("Sophie complained the light in her room was ___, making it "
             "difficult to read.", "dim"),
        ],
        "comprehension": [
            "Why does Naima's father no longer come home for lunch?",
            "What does Naima's mother say when the aunts ask about Naima crashing "
            "the rickshaw?",
            "What is the only thing Naima can picture when she closes her eyes?",
            "What does Naima allow herself to admit about the revised alpanas?",
            "How does Naima plan to earn the money for the rickshaw's repairs?",
            "Why does Naima give Saleem the white ribbon from her braid?",
            "What does Naima force herself to not think about?",
        ],
        "writing_prompt": (
            "In the past, Naima has had some crazy ideas that ended up working "
            "out really well, and others that turned out pretty badly. Write "
            "about a crazy idea you have had. How did it turn out? Did you "
            "surprise yourself or others with the results?"
        ),
        "discussion": [
            "Why isn't Naima behaving like herself? How does your behavior change "
            "depending on your mood?",
            "Why does her mother's faded saree make Naima sad? Considering what "
            "we know about Naima's mother, how important do you think getting a "
            "new saree is to her?",
            "Why do you think Naima's father asked her to improve the alpanas on "
            "their hut? What does he mean when he says, “Don't do it for the "
            "prize. Make them right for their sake”? Have you ever done something "
            "for its own sake, regardless of the prize?",
            "Why do you think Naima's revised alpanas turned out better than the "
            "ones she would have painted from scratch?",
            "Why does Naima give Saleem her white ribbon? Why do you think they "
            "value each other's friendship?",
            "Why does Naima enjoy the freedom that comes with being disguised as "
            "a boy?",
            "When Naima says she wants a job at the rickshaw shop, how does the "
            "boy she meets respond? Why do you think he responds like this?",
            "What might Naima be thinking when she finds out the widow is the "
            "repairman?",
        ],
    },
    {
        "number": 4,
        "chapters": "Chapters 11–Author's Notes",
        "characters": ["Naima", "The Widow", "Mother", "Father"],
        "definitions": [
            "polite, moral, and honest",
            "feeling or expressing great joy",
            "wild or threatening",
            "feeling or showing fear and worry",
            "to find fault noisily or angrily",
            "to move or work with effort",
        ],
        "vocab": [("decent", 1), ("fierce", 3), ("frantic", 4),
                  ("jubilant", 2), ("labor", 6), ("scold", 5)],
        "blanks": [
            ("The ___ dog barked wildly when the mail carrier delivered the "
             "package.", "fierce"),
            # The guide's sentence needs the past tense of the listed word.
            ("Nate felt sad after being ___ for playing a mean trick on his "
             "little sister.", "scolded"),
            ("A ___ person does not lie, cheat, or steal in order to get what "
             "they want.", "decent"),
            ("The mom is ___ when her kids dawdle around the house in the "
             "morning, making her late to work.", "frantic"),
            ("Everyone felt ___ at the wedding!", "jubilant"),
            ("The water buffalo ___ under the heavy load.", "labored"),
        ],
        "comprehension": [
            "What is Naima shocked to discover about the widow?",
            "What does the widow explain about the women's bank?",
            "How many panels does the widow allow Naima to work on?",
            "Why does the widow tell Naima's father not to scold her?",
            "What does Naima's father do after the shock of discovering the "
            "widow's identity?",
            "Why does the widow let Naima's father borrow her rickshaw for the "
            "day?",
            "What is Naima and Saleem's secret-keeping policy?",
        ],
        "writing_prompt": (
            "In the Author's Note, Mitali Perkins explains how microfinance is "
            "being used to help fight poverty. Create your own example of where "
            "you think microfinance funds would be useful."
        ),
        "discussion": [
            "What feels like the most important question in the world to Naima? "
            "Why do you think it's important to her considering what we've "
            "learned about the role of women in her village?",
            "Why do you think Naima's father was so angry when he finally found "
            "her, even though he hadn't been angry when she crashed the rickshaw?",
            "How does Naima's father prove to her that he believes daughters are "
            "just as good as sons?",
            "What do you think becoming a trained rickshaw repairwoman will mean "
            "for Naima's life? How will people in the village react when they "
            "find out? How will learning a trade help Naima in the future?",
            "What do you think about Naima and Saleem's secret keeping policy?",
            "Why does it mean so much to Naima when people say it is a good thing "
            "that she turned out to be a girl?",
        ],
    },
]

# Section 5 — the guide's own list, each paired with a short name so a child
# can scan the six options instead of reading 233 words of prose.
FINAL_PROJECT_INTRO = "Complete one or more of the following assignments."
FINAL_PROJECT_OPTIONS = [
    ('Tradition poster',
     'Naima and her family are very proud of the beauty of their culture, and they express their pride by painting alpanas. What is a tradition your family is proud of? Create a poster to share this tradition.'),
    ('Paint a rickshaw panel',
     'Painting both alpanas and rickshaws is an important part of Bangladesh culture. Research alpanas and rickshaw art. Paint your own rickshaw panel inspired by these images.'),
    ('Bangla word cloud',
     'The Glossary contains a list of Bangla words. Create a word cloud poster with these words arranged colorfully. Create a border for your poster similar to the chapter headings in the book.'),
    ('The one-hour walk',
     "Naima has to walk for an hour to reach the village of the rickshaw repair shop. With an adult, go on a one-hour walk, and see how far you are able to travel. Write about your experience. How many miles did you go? Where did you end up? What did you see along the way? Do you feel like you learned anything about Naima's life, or what it would be like to not have access to cars?"),
    ('Build a diorama',
     'Build a diorama of your favorite scene in the book.'),
    ('Thankful poster',
     "Naima had to give up going to school because her family couldn't afford to send both her and her sister. Create a poster showing some of the things your family provides for you that you are thankful for."),
]


def section_by_number(number):
    return next((s for s in SECTIONS if s["number"] == number), None)


def matching_key(section):
    """The guide's answer key for the matching exercise: word -> definition no."""
    return {word: n for word, n in section["vocab"]}
