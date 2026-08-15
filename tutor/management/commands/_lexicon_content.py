"""Operation Lexicon: Traits of Character (Blackbird & Company, Grade 3).

Transcribed from the family's purchased guide for private use, like the other
Blackbird units here.

The shape of every week is identical: listen to a picture-book biography of a
real person, meet ten words that describe THAT person, use each one to finish a
sentence about them, then write three things that amazed you. Ten weeks, a
hundred words, and a poster that fills in as she goes.

The words are anchored to a person on purpose — "inquisitive" attached to a man
who would not stop asking about prime numbers is a word that sticks, where a
word on a list is not.

NOTE markers flag text reconstructed from a garbled extraction (the guide prints
its definition boxes under decorative artwork). Those are worth a glance against
the printed copy; everything else is verbatim.
"""

# Each week: the person, what they did, the book, and the ten words.
# Sentences are (text_with_____, answer). The blank is five underscores.
WEEKS = [
    {
        "number": 1,
        "person": "Paul Erdős",
        "role": "Mathematician",
        "book": "The Boy Who Loved Math: The Improbable Life of Paul Erdős",
        "author": "Deborah Heiligman",
        "illustrator": "LeUyen Pham",
        "words": [
            ("focused", "Someone who is focused is attentive to an activity at hand."),
            ("generous", "Generous people are liberal in giving and sharing."),
            ("genius", "A genius has an exceptional natural capacity of intellect."),
            ("homeschooled", "A homeschooled person is educated at home."),
            ("impatient", "An impatient person is not able to accept delay."),
            ("inquisitive", "Inquisitive people are eager for knowledge."),
            ("mathematical", "Someone who is mathematical is intrigued by and interested in math."),
            ("playful", "Playful people are frolicsome and full of fun."),
            ("social", "Being social is exemplified by friendly companionship."),
            ("unruly", "An unruly person does not care for rules."),
        ],
        "sentences": [
            ("It is obvious that Paul Erdős was a _____ boy because his favorite "
             "pastime was exploring numbers.", "mathematical"),
            # NOTE: sentences 2-5 were partly obscured in the source; wording
            # reconstructed from the visible fragments and the book's events.
            ("_____ Paul hated to be told what to do at home and at school!", "unruly"),
            ("Paul was _____, taught at home by his mother rather than at school.",
             "homeschooled"),
            ("_____ Paul could not sit still and wait for others to finish.", "impatient"),
            ("_____ on numbers, Paul thought about math almost all the time.", "focused"),
            ("_____ Paul had a lot of questions about prime numbers.", "inquisitive"),
            ("When Paul attended high school he became _____ and made many friends "
             "with people his own age.", "social"),
            ("Once, _____ Paul opened a tomato carton by stabbing it with a knife.",
             "playful"),
            ("Early on, Paul was considered a _____ mathematician, even though simple "
             "tasks, like buttering bread, were difficult.", "genius"),
            ("Paul Erdős was _____ with his math knowledge and helped connect "
             "mathematicians all over the world.", "generous"),
        ],
    },
    {
        "number": 2,
        "person": "Frank Lloyd Wright",
        "role": "Architect",
        "book": "The Shape of the World: A Portrait of Frank Lloyd Wright",
        "author": "K. L. Going",
        "illustrator": "Lauren Stringer",
        "words": [
            ("appreciative", "An appreciative person is able to care and be thankful."),
            ("artistic", "An artistic person shows skill and excellence in creative ability."),
            ("awestruck", "Awestruck is to be filled with an awesome sense of wonder."),
            ("benevolent", "A benevolent person is able to express goodwill and kindness."),
            ("curious", "A curious person is eager to discover and learn."),
            ("determined", "A determined person is firm in purpose and will not give up."),
            ("hardworking", "To be hardworking is to work with steady effort."),
            ("imaginative", "An imaginative person forms new and original ideas."),
            ("impressive", "An impressive person makes a strong and lasting impression."),
            ("observant", "An observant person is quick to notice and pay attention."),
        ],
        "sentences": [
            ("_____ Frank Lloyd Wright saw shapes everywhere he looked, even shapes "
             "within shapes!", "observant"),
            ("Spending summers on his Uncle's farm, Frank became _____.", "hardworking"),
            ("Frank was often _____ as he looked with amazement upon the great big "
             "world around him.", "awestruck"),
            ("Always _____, Frank asked himself many questions as he observed the world.",
             "curious"),
            ("As an architect, Frank Lloyd Wright was _____, always working hard, never "
             "forgetting the hills and prairies of his childhood and the encouragement "
             "of his mother.", "determined"),
            ("_____ Frank created gorgeous geometric windows and beautiful buildings "
             "inspired by nature.", "artistic"),
            ("When he grew older, _____ Frank looked back on his accomplishments with "
             "pride.", "appreciative"),
            ("_____ Frank built a honeycomb house, a museum in the shape of a snail, "
             "and towers like trees.", "imaginative"),
            ("_____ Frank left the world many gifts.", "benevolent"),
            ("The life accomplishments of Frank Lloyd Wright are _____.", "impressive"),
        ],
    },
    {
        "number": 3,
        "person": "Vasya Kandinsky",
        "role": "Artist",
        "book": "The Noisy Paint Box: The Colors and Sounds of Kandinsky's Abstract Art",
        "author": "Barb Rosenstock",
        "illustrator": "Mary GrandPré",
        "words": [
            ("ambitious", "To be ambitious is to be eager and motivated."),
            ("bored", "To be bored is to feel unhappy and disinterested."),
            ("brave", "A brave person shows great mental or moral strength."),
            ("compliant", "A compliant person goes along with the wishes of others."),
            ("engaged", "An engaged person is deeply involved and interested."),
            ("exuberant", "An exuberant person is filled with lively energy and joy."),
            ("innovative", "To be innovative is to introduce new ideas and methods."),
            ("perceptive", "A perceptive person notices and understands quickly."),
            ("studious", "To be studious is to be devoted to study."),
            ("synesthete", "A synesthete experiences one sense through another, such as "
                           "hearing colors."),
        ],
        "sentences": [
            ("As a _____, Vasya Kandinsky experienced colors as sounds and sounds as "
             "colors.", "synesthete"),
            ("When the adults would talk and talk, Vasya would become _____.", "bored"),
            ("_____ Vasya worked hard to learn math, science, history, and music.",
             "studious"),
            ("Vasya was very _____ with the colors he was mixing from the paintbox his "
             "aunt gave him.", "engaged"),
            ("Vasya was _____ to quit his teaching job to become a painter in Munich.",
             "brave"),
            ("Being _____ and painting what his teachers wanted made Vasya Kandinsky "
             "unhappy.", "compliant"),
            ("_____ Kandinsky, determined to paint the colors he heard.", "ambitious"),
            ("_____ Vasya delighted as he painted the sound of colors.", "exuberant"),
            ("_____ Kandinsky created a new form of art.", "innovative"),
            ("Focused and _____, Kandinsky connected his paintings to music by naming "
             "them after the music he loved.", "perceptive"),
        ],
    },
    {
        "number": 4,
        "person": "Antoni Gaudí",
        "role": "Architect",
        "book": "Building on Nature: The Life of Antoni Gaudí",
        "author": "Rachel Rodriguez",
        "illustrator": "Julie Paschkis",
        "words": [
            ("arthritic", "To be arthritic is to be afflicted by arthritis, a painful "
                          "disease of the joints."),
            ("bold", "A bold person is fearless and courageous."),
            ("clever", "To be clever is to show inventiveness and ingenuity."),
            ("dreamer", "A dreamer is a person whose ideas are visionary."),
            ("elegant", "An elegant person is tasteful and refined."),
            ("industrious", "An industrious person works hard and steadily."),
            ("reader", "A reader is a person who reads."),
            ("tenacious", "A tenacious person holds on and does not let go."),
            ("watchful", "A watchful person observes closely and carefully."),
            ("whimsical", "A whimsical person is playfully fanciful."),
        ],
        "sentences": [
            ("Little _____ Gaudí often suffered from achy bones and joints.", "arthritic"),
            ("Always _____, he noticed light and form and the wonder of nature.",
             "watchful"),
            ("As a boy, _____ Gaudí imagined rebuilding a monastery that was in ruins.",
             "dreamer"),
            ("After high school, _____ Gaudí worked hard to become an architect.",
             "industrious"),
            ("Being a _____, he learned much from books.", "reader"),
            ("_____ Gaudí wears fine, stylish clothes and accessories and extends this "
             "appreciation for beauty to his architectural designs.", "elegant"),
            ("While some people would stop and stare, not understanding, Vicens House "
             "is evidence that Gaudí was _____.", "bold"),
            ("_____ Gaudí even designed a bedbug into the door knocker!", "whimsical"),
            ("_____ Gaudí found new ways to build what no one had built before.",
             "clever"),
            ("Because Gaudí was _____, he studied the giant problem of building an "
             "underground chapel for 10 years!", "tenacious"),
        ],
    },
    {
        "number": 5,
        "person": "Josef Albers",
        "role": "Artist",
        "book": "An Eye for Color: The Story of Josef Albers",
        "author": "Natasha Wing",
        "illustrator": "Julia Breckenreid",
        "words": [
            ("avant-garde", "To be avant-garde is to be first to create an original idea."),
            ("colorist", "A colorist is someone who deals with the science and art of color."),
            ("creative", "A creative person is marked by artistic ability."),
            ("discerning", "To be discerning is to demonstrate insight and understanding."),
            ("influential", "An influential person is able to build confidence and "
                            "direct others."),
            ("meticulous", "To be meticulous is to take precise care with details."),
            ("orderly", "An orderly person is neat and arranges things with care."),
            ("poor", "To be poor is to have little money or few possessions."),
            ("prolific", "A prolific person produces a great deal of work."),
            ("teacher", "A teacher is a person who helps others learn."),
        ],
        "sentences": [
            ("Josef Albers was considered _____ in the field of color because he was "
             "not afraid to experiment.", "avant-garde"),
            ("_____ Josef saw art in the simple things, especially the way pottery and "
             "the colors of buildings looked under the Mexican sun.", "discerning"),
            ("_____ Joseph saw beauty and potential in the doors his father painted.",
             "creative"),
            ("During his studies, being a _____ student who could not afford supplies "
             "didn't stop him from art-making.", "poor"),
            ("Josef Albers was _____ in his study of color, taking care to learn as a "
             "scientist.", "meticulous"),
            ("_____ Josef used the simplicity of the square to keep the focus on color "
             "instead of shape.", "orderly"),
            ("A _____ artist, he painted more than a thousand of these squares!",
             "prolific"),
            ("_____ Joseph eventually published a book about his color discoveries.",
             "colorist"),
            ("As a _____, Josef showed his students how to see color for themselves.",
             "teacher"),
            ("Writer, teacher, artist, Josef Albers continues to be _____ in the work "
             "of young and old artists alike.", "influential"),
        ],
    },
    {
        "number": 6,
        "person": "Maria Merian",
        "role": "Naturalist",
        "book": "Summer Birds: The Butterflies of Maria Merian",
        "author": "Margarita Engle",
        "illustrator": "Julie Paschkis",
        "words": [
            ("accurate", "To be accurate is to be correct in all details."),
            ("antipathetic", "To be antipathetic is to feel strongly against something."),
            ("aspirational", "An aspirational person wants to achieve success."),
            ("careful", "A careful person is attentive to danger, and watchful."),
            ("conscientious", "To be conscientious is to be guided by a sense of right "
                              "and wrong."),
            ("empirical", "To be empirical is to be concerned with observation and data."),
            ("exacting", "To be exacting is to make great demands on one's skills."),
            ("intentional", "An intentional person acts deliberately, on purpose."),
            ("sedulous", "A sedulous person accomplishes tasks with perseverance."),
            ("young", "A young person has lived for only a short time."),
        ],
        "sentences": [
            ("Maria was _____, often sitting still to observe her butterflies.",
             "careful"),
            ("_____ Maria purposefully kept caterpillars and summer birds in boxes and "
             "jars, well fed with leaves as she studied them.", "intentional"),
            ("Maria, being _____, persevered to proclaim her idea that insects are not "
             "evil.", "sedulous"),
            ("Maria was _____, using her artistic skill to fill her notebook with "
             "precise paintings of her butterfly observations.", "accurate"),
            ("_____ Maria worked diligently, using her artistic ability to communicate "
             "all she learned about butterflies, so one day everyone would know the "
             "truth about butterflies.", "aspirational"),
            ("Because Maria was _____, she worked hard over time to successfully "
             "communicate the truth about butterflies.", "exacting"),
            ("_____ Maria was motivated to observe butterflies and communicate what she "
             "learned because she disagreed with the wrong view that insects are evil.",
             "antipathetic"),
            ("Beginning at a _____ age, Maria demonstrated an aptitude for art and an "
             "interest in the natural world.", "young"),
            ("_____ Maria felt strongly that summer birds are beautiful and harmless.",
             "conscientious"),
            ("_____ Maria Merian's careful observations and experience with butterflies "
             "enabled her to communicate scientific information about the beautiful "
             "animals.", "empirical"),
        ],
    },
    {
        "number": 7,
        "person": "Henrietta Leavitt",
        "role": "Astronomer",
        "book": "Look Up! Henrietta Leavitt, Pioneering Woman Astronomer",
        "author": "Robert Burleigh",
        "illustrator": "Raúl Colón",
        "words": [
            ("amazed", "An amazed person is greatly surprised and astounded."),
            ("discoverer", "To be a discoverer is to be the first person to find a "
                           "scientific phenomena."),
            ("eager", "An eager person wants to do or have something very much."),
            ("important", "An important person is of great significance or value."),
            ("intelligent", "An intelligent person possesses a high level of mental "
                            "capacity."),
            ("mindful", "A mindful person is conscious or aware of something."),
            ("pioneering", "To be pioneering is to bring new ideas into the world."),
            ("star-gazer", "A star-gazer is a person who studies the night sky."),
            ("theorizer", "A theorizer creates the premise on which others build."),
            ("thoughtful", "A thoughtful person is reflective and considers deeply."),
        ],
        "sentences": [
            ("_____ Henrietta wanted very much to know everything about the "
             "\"wonderful bigness\" of all she saw.", "eager"),
            ("As she studied astronomy, Henrietta grew more and more _____ by the "
             "astoundingly vast distances light can travel.", "amazed"),
            ("_____ Henrietta was the first person to pay attention to the phenomenon "
             "of the star blink-time pattern.", "discoverer"),
            ("Henrietta was _____, and used her mental capacity to observe and learn "
             "about the universe.", "intelligent"),
            ("_____ Henrietta was so keenly aware of the stars, she imagined they were "
             "trying to speak to her.", "mindful"),
            ("_____ Henrietta contributed new ideas to the field of astronomy.",
             "pioneering"),
            ("_____ Henrietta peered contemplatively through microscopes to measure star "
             "dots, believing she would discover something.", "thoughtful"),
            ("Because Henrietta looked steadily, intently, and purposefully at the sky, "
             "this _____ continued to question, \"How high is the sky?\"", "star-gazer"),
            ("Henrietta Leavitt is an _____ scientist, and made a huge contribution to "
             "the field of astronomy.", "important"),
            ("_____ Henrietta's discoveries created the framework for other scientists "
             "to contribute ideas, and build upon the way distances are measured in "
             "space.", "theorizer"),
        ],
    },
    {
        "number": 8,
        "person": "Margaret E. Knight",
        "role": "Inventor",
        "book": "Marvelous Mattie: How Margaret E. Knight Became an Inventor",
        "author": "Emily Arnold McCully",
        "illustrator": "Emily Arnold McCully",
        "words": [
            ("brainstormer", "A brainstormer is someone who brings first shape to a "
                             "clever idea."),
            ("businesswoman", "A businesswoman is a woman who works in business "
                              "especially as an executive."),
            ("deliberate", "To be deliberate is to engage in thorough, careful, and "
                           "decisive consideration."),
            ("developer", "A developer is a person who innovates."),
            ("ingenious", "An ingenious person is clever and inventive."),
            ("lonely", "A lonely person is isolated and alone."),
            ("maker", "A maker is a person who makes or produces something from scratch."),
            ("original", "An original person is someone who has new ideas."),
            ("resolute", "A resolute person is determined and firm of purpose."),
            ("unusual", "An unusual person is uncommon and out of the ordinary."),
        ],
        "sentences": [
            ("_____ Mattie kept all her ideas in her My Inventions notebook.",
             "brainstormer"),
            ("Mattie the _____ made a whirligig, a jumping jack, and a foot warmer for "
             "members of her family.", "maker"),
            ("Sometimes, like when she made a kite for Charlie and Jim, people thought "
             "her _____.", "unusual"),
            ("Mattie was _____ when her family was gone for thirteen hours a day working "
             "at the textile mills in Manchester.", "lonely"),
            ("_____ Mattie thought of a stop-motion device no one had imagined before.",
             "original"),
            ("Being _____, Mattie purposefully hired a lawyer to go to court and prove "
             "her machine design had been stolen.", "resolute"),
            ("_____ Mattie worked and worked, carefully and decisively, to solve the "
             "problem of creating a machine that could make a square-bottom paper bag.",
             "deliberate"),
            ("_____ Mattie invested her energy and talent to innovate and solve many "
             "problems.", "developer"),
            ("Refusing to sell her paper bag patent and setting up the Eastern Paper Bag "
             "Company was the beginning of becoming a leading _____.", "businesswoman"),
            ("Being an inventor, _____ Mattie valued and brought shape to her ideas.",
             "ingenious"),
        ],
    },
    {
        "number": 9,
        "person": "Grace Hopper",
        "role": "Computer Scientist",
        "book": "Grace Hopper: Queen of Computer Code",
        "author": "Laurie Wallmark",
        "illustrator": "Katy Wu",
        "words": [
            ("brilliant", "A brilliant person is intellectually or creatively talented."),
            ("decorated", "To be decorated is to be given special honor for service."),
            ("insatiable", "To be insatiable is to be impossible to satisfy."),
            ("intrepid", "To be intrepid is to be fearless and unafraid."),
            ("jokester", "A jokester is a person fond of making jokes."),
            ("meticulous", "To be meticulous is to show great attention to detail."),
            ("problem-solver", "A problem-solver is a person who solves unsettled "
                               "questions."),
            ("questioning", "A questioning person is inquisitive, desiring answers."),
            ("scientific", "To be scientific is to reason using evidence and testing."),
            ("unconventional", "An unconventional person does not conform to what is "
                               "generally done."),
        ],
        "sentences": [
            ("_____ Grace checked every detail of the code that would guide Navy "
             "missiles, line by line, over and over again.", "meticulous"),
            ("Because she was a _____, Grace wanted computers to participate in the work "
             "of writing new code.", "problem-solver"),
            ("_____ Grace tested her ideas the way a scientist would, over and over.",
             "scientific"),
            ("After figuring out how clocks work, _____ Grace fearlessly moved on to "
             "bigger challenges.", "intrepid"),
            ("_____ Grace's room overflowed with books and equipment.", "questioning"),
            ("_____ Grace loved playing pranks on her coworkers.", "jokester"),
            ("Even though she failed Latin, _____ Grace wanted to pursue her "
             "mathematical talent and intentionally pressed into studying until she "
             "passed.", "brilliant"),
            ("Grace's _____, unquenchable desire to solve problems made her really good "
             "at her work.", "insatiable"),
            ("_____ Grace rigged her clock to run backward.", "unconventional"),
            ("\"Queen of the Computer Code,\" Grace Hopper became a _____ Admiral after "
             "her death, having been awarded the Presidential Medal of Freedom.",
             "decorated"),
        ],
    },
    {
        "number": 10,
        "person": "Wangari Maathai",
        "role": "Environmentalist",
        "book": "Mama Miti: Wangari Maathai and the Trees of Kenya",
        "author": "Donna Jo Napoli",
        "illustrator": "Kadir Nelson",
        "words": [
            ("caretaker", "A caretaker is someone who cares for someone or something."),
            ("compassionate", "A compassionate person shows concern for others."),
            ("ecologist", "An ecologist is an expert in the study of living things and "
                          "their environment."),
            ("educator", "An educator is a person who is skilled at teaching."),
            ("encouraging", "An encouraging person offers support and confidence."),
            ("environmentalist", "An environmentalist is a person who works to protect "
                                 "the environment."),
            ("leader", "A leader is a person who commands a group."),
            ("Nobel Laureate", "A Nobel Laureate is someone who has been awarded a Nobel "
                               "Prize."),
            ("peacemaker", "A peacemaker is a person who brings peace through "
                           "negotiation."),
            ("wise", "A wise person has knowledge and good judgement."),
        ],
        "sentences": [
            ("_____ Wangari always remembered her roots and was eager to share with "
             "others her knowledge of trees and her message of peace with nature.",
             "educator"),
            ("_____ Wangari showed concern for the poor who crossed her path.",
             "compassionate"),
            ("_____ Wangari gave people confidence by reminding them of their own "
             "strength.", "encouraging"),
            ("\"Thayu nyumba,\" or \"Peace, my people,\" said _____ Wangari.", "wise"),
            ("Wangari Maathai was the first African woman to be decorated as a _____ for "
             "her contribution to sustainable development, democracy and peace.",
             "Nobel Laureate"),
            ("Because she was an expert, _____ Wangari always knew the best tree to "
             "suggest.", "ecologist"),
            ("Wangari, _____, introduced and advocated for the planting of trees for "
             "peace.", "peacemaker"),
            ("Wangari is a _____, and her work embodies \"harambee,\" the spirit of "
             "pulling together for the common good.", "leader"),
            ("_____ Wangari cared for Kenya, tree by tree.", "caretaker"),
            ("_____ Wangari imagined a green belt of peace, and taught others to care "
             "about her idea.", "environmentalist"),
        ],
    },
]


def all_words():
    """The full hundred, in the order she meets them — the poster's order."""
    out = []
    for week in WEEKS:
        for word, _definition in week["words"]:
            out.append(word)
    return out
