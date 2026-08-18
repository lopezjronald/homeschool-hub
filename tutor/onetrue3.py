"""One True Sentence, Volume C3: Tools of Style #3 — the guide's content.

Blackbird & Company, by Kimberly Bredberg, MFA and Sara Evans. Twenty weeks of
sentence craft: each week introduces one rhetorical device (this volume moves
past C1's basics into the classical figures — antanagoge, parataxis, aporia,
synecdoche…), shows it working in a model sentence, then asks for five of the
student's own.

Same shape as tutor/onetrue.py (Volume C1), which the seed already knows how
to build from:

    topic            the tool of style this week teaches
    explanation      the guide's own definition of it
    example          an optional worked example with its source
    sentence_one     the model sentence she copies out, and where it is from
    sentence_two     a second sentence, used for the noticing questions
    questions_two    what to notice in sentence two
    questions_one    what to notice in sentence one
    note             an optional warning where the printed guide is wrong
                     in a way she would otherwise copy or reason from
    practice         the "Now you try!" groups

THE COPYING IS DONE BY HAND, exactly as in Volume C1.

SHAPE NOTE: unlike C1, this volume prints ONE model sentence per week, in an
"Example:" box with no citation, and the numbered lesson tasks include "Copy
the example sentence." That box is therefore the copy model: its text lives in
sentence_one (citation ""), copy_instruction is the printed copy task, example
is None so the sentence is not rendered twice, and the remaining numbered
tasks are questions_one in printed order. There is no Sentence 2 anywhere in
this volume: sentence_two is None and questions_two is [] in every week.

NUMBERING: the guide numbers its own weeks "Week 1" through "Week 20" in the
lesson headings and running heads — it does NOT continue Volume C1's count.
The `number` field below is the number as printed in this volume.

Transcribed by reading the rendered pages (150 dpi); this PDF's text layer is
scanner OCR garbage ("Tools of Style �3") and was used for navigation only.

Printed quirks preserved verbatim (see also the per-week "note" fields):
  - Basics Part 2 prints "blare … means to make or admit a very loud, raucous
    noise" — "admit" for "emit".
  - Basics Part 3 prints "the caterpilar is alive" — "caterpillar" misspelled.
  - Basics Part 5 prints "the type of verb that is used in the ordinate" —
    "ordinate" where "predicate" is meant.
"""

CURRICULUM_NAME = "One True Sentence: Tools of Style #3"

EPIGRAPH = ("All you have to do is write one true sentence. Write the truest "
            "sentence that you know.", "Ernest Hemingway")

FOR_THE_TEACHER = """Learning to write well requires tools that are best
acquired through the process of discovery. One True Sentence is an opportunity
for students to discover the wonder of writing and to simultaneously gain tools
as they construct ideas into sentences. All instructions are embedded in the
weekly lessons. Over the course of twenty weeks, students will be introduced to
and review literary devices, elements of style, mechanics, and grammar. Along
the way, they will learn to appreciate and delight in the art of crafting
sentences."""

HOW_IT_TEACHES = """Each week students will be introduced to a rhetorical term
that will be directly explained and followed by an example. Encourage students
to read and study the information carefully. It is useful, when being
introduced to the new rhetorical term, to use the internet to explore the
word's origin and to also listen to the word's pronunciation. After this simple
direct instruction, students are guided into applicational exercises. Over
time, as they explore the mechanics, grammar, and style of model sentences,
they will begin to recognize and utilize the elements great writers use to
construct savvy sentences. Constructing sentences, week after week, moves
students boldly toward effortless and effective communication."""

# "Sentence Construction Basics to Remember" — printed pages 8-9, bodies
# condensed as in the C1 module, examples kept as printed (including the
# printed errors, flagged with comments).
BASICS = [
    {
        "part": "Part 1: Four Types of sentences",
        "body": "Declarative sentences state something — fact or opinion or "
                "imagination. Imperative sentences implore or command, "
                "sometimes so much so that you need an exclamation point. "
                "Exclamatory sentences express strong emotion — joy, anger, "
                "sorrow, shock, disbelief. Interrogative sentences always ask, "
                "and questions always end in a special mark.",
        "examples": ["The cat purrs.",
                     "Sassy, the calico cat that we rescued, often falls asleep "
                     "in the sun purring."],
    },
    {
        "part": "Part 2: Words",
        "body": "All sentences are constructed with words. Each word has a "
                "specific meaning and a specific role to play. The guide's "
                "example: \"blare\" in its verb form means to make or admit a "
                "very loud, raucous noise (so the guide prints — it means "
                "\"emit\"); its noun form, \"blaring,\" is the noise itself. "
                "The guide recommends using a dictionary often when "
                "constructing sentences.",
        "examples": ["The alarm clock blared a horrible screeching sound.",
                     "The blaring of the horns during rush hour is exhausting."],
    },
    {
        "part": "Part 3: Phrases",
        "body": "A phrase is a small group of words standing together as a "
                "conceptual unit that is neither the subject nor the "
                "predicate, and never stands alone as a sentence. Phrases are "
                "the wonderful details that make sentences sing. The five "
                "types are noun, verb, adjective, adverb and prepositional.",
        # "caterpilar" is as printed in the guide.
        "examples": ["Skipping stones into the sea, she smiled.",
                     "walk to the blue house · the fish was caught, the "
                     "caterpilar is alive · deep menacing blue · sung sweetly, "
                     "right here · under the rock, over there, around the "
                     "corner"],
    },
    {
        "part": "Part 4: Clauses",
        "body": "Every sentence has one. A clause is a group of words that has "
                "both a subject and a predicate. An independent clause makes "
                "sense by itself because it expresses a complete thought; a "
                "dependent clause does not.",
        "examples": ["The child was happy.",
                     "Because the sun was shining",
                     "Because the sun was shining, the child was happy."],
    },
    {
        "part": "Part 5: Patterns",
        "body": "All sentences fall into five to ten basic subject/predicate "
                "patterns. The subject is what the sentence is about; the "
                "predicate contains the verb or verb phrase, plus any direct "
                "or indirect object. The patterns are typically distinguished "
                "by the type of verb that is used in the ordinate (so the "
                "guide prints — \"predicate\" is meant).",
        "examples": ["The dog slept.", "The dog chased a cat.",
                     "The dog slept peacefully.", "The dog is called Theo.",
                     "The dog brings the family happiness."],
    },
]

WEEKS = [
    {
        "number": 1,
        "topic": "Antanagoge",
        "explanation_label": "Explanation",
        "explanation": "A device that writers use to downplay an undesirable "
                       "situation—making lemonade from lemons.",
        # The guide's "Example:" box is the copy model; it lives in
        # sentence_one (see module docstring). No citation is printed.
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "Though the torrential downpour may flood the streets, it "
                    "signals a mild summer ahead with warm days and clear "
                    "skies.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of antanagoge. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word antanagoge.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "What is the undesirable situation in the example sentence?",
            "How is this situation being downplayed?",
            "Rewrite the sentence using the same undesirable situation but "
            "downplayed in a different way.",
        ],
        "practice": [
            {"instruction": "Craft 5 original sentences using antanagoge.\n"
                            "Begin by thinking of a situation that is, to "
                            "you, undesirable, then use antanagoge to "
                            "downplay the situation.",
             "count": 5},
        ],
    },
    {
        "number": 2,
        "topic": "Understatement",
        "explanation_label": "Explanation",
        "explanation": "Understatement expresses an idea in a way that is "
                       "less important than it is in reality.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        # The comma after "was" is as printed.
        "sentence_one": {
            "text": "Though the thermometer read 103 degrees, Bobby declared "
                    "the day was, “a little on the warm side.”",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of understatement. (if needed, "
            "listen to the pronunciation on the internet.)",
            "Research the history of the word understatement.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "What is being understated in the example sentence?",
            "Rewrite the sentence, exaggerating the subject instead of "
            "understating it.",
            "How does this change the tone of the sentence?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using "
                            "understatements.",
             "count": 5},
        ],
    },
    {
        "number": 3,
        "topic": "Parataxis",
        "explanation_label": "Explanation",
        # The gray box carries a "Reminder:" block after the definition; kept
        # inline with line breaks.
        "explanation": "When crafting sentences, writers sometimes use "
                       "parataxis, listing clauses or phrases one after "
                       "another to indicate relationship—coordination or "
                       "subordination.\n"
                       "Reminder:\n"
                       "Clause — a sentence part that contains a subject and "
                       "a verb. (may operate independently or dependently).\n"
                       "Phrase — a sentence part that contains a small group "
                       "of words that forms a conceptual unit.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "The city was alive with sounds, the blaring of horns, "
                    "the whistling of wind between buildings, the cacophony "
                    "of voices, the crumple of tires on asphalt.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of parataxis. (if needed, listen "
            "to the pronunciation on the internet)",
            # "the word of parataxis" is as printed — a doubled "of".
            "Research the history of the word of parataxis.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "List the clauses in the example sentence.",
            "List the phrases in the example sentence.",
            "What senses are evoked in the example sentence?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using parataxis.\n"
                            "Think of a familiar place. Now describe that "
                            "place listing attributes with clauses and "
                            "phrases like in the example on the previous "
                            "page.",
             "count": 5},
        ],
    },
    {
        "number": 4,
        "topic": "Euphemism",
        "explanation_label": "Explanation",
        "explanation": "Writers use this device to communicate something "
                       "harsh in a more mild, indirect way.",
        # The box prints two labels: "Examples:" (this idiom list) and then
        # "Example sentence:" (the copy model, in sentence_one).
        "example": {
            "text": "Kick the bucket. Pushing up daisies. Passed on. Nuclear "
                    "exchange. Letting someone go. Over the hill. Lost his "
                    "marbles. Lose your lunch. Between jobs.",
            "citation": "",
        },
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "Instead of putting candles on Grandpa’s cake, his "
                    "friends wrote, “Congratulations on Making It Over the "
                    "Hill,” in frosting.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of euphemism. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word euphemism.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "What is the euphemism in the example sentence?",
            "What does the euphemism mean?",
            # "Re-write" is hyphenated in print this week ("Rewrite" in
            # Week 1) — kept as printed.
            "Re-write the sentence using a new euphemism.",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using "
                            "euphemisms.\n"
                            "Use the list of common euphemisms on the "
                            "previous page, or use your own.",
             "count": 5},
        ],
    },
    {
        "number": 5,
        "topic": "Parenthesis",
        "explanation_label": "Explanation",
        "explanation": "Parenthesis is a device writers use to insert an "
                       "aside or an additional idea into the flow of context.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "Our neighbor, Mr. Barton, yelled at Duncan (my dog) "
                    "because he dug a hole under the fence.",
            "citation": "",
        },
        "sentence_two": None,
        "note": "The heading and the explanation spell the device "
                "“parenthesis,” but every task below and the practice page "
                "print “paranthesis” with an a — that spelling is the "
                "guide's mistake, kept as printed. The word is spelled "
                "parenthesis.",
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of paranthesis. (if needed, "
            "listen to the pronunciation on the internet)",
            "Research the history of the word paranthesis.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "Rewrite the sentence as two sentences instead of using "
            "paranthesis.",
            "Which conveys the information best? Why?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using "
                            "paranthesis.",
             "count": 5},
        ],
    },
    {
        "number": 6,
        "topic": "Amplification",
        "explanation_label": "Explanation",
        "explanation": "Amplification adds detail to an idea already "
                       "expressed.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "The weather was perfect for a picnic—the sun smiled "
                    "brightly, and a soft breeze tickled the leaves over our "
                    "heads.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of amplification. (if needed, "
            "listen to the pronunciation on the internet)",
            "Research the history of the word amplification.",
            # Plural "sentences … them" is as printed this week, though the
            # box holds one sentence.
            "Read the example sentences silently, then read them again, "
            "slowly, in a whispered tone.",
            "Underline the amplification in the example sentence and write "
            "it here.",
            "Now rewrite the sentence replacing these words with a brand new "
            "amplification of the weather.",
            "What would the sentence be like without amplification? Why?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using "
                            "amplification.\n"
                            "Hint: Begin with a memory or a situation.\n"
                            "The new bike was perfect—a ten speed painted "
                            "with blue sparkles.",
             "count": 5},
        ],
    },
    {
        "number": 7,
        "topic": "Ellipsis",
        "explanation_label": "Explanation",
        "explanation": "Ellipsis is the deliberate omission of superfluous "
                       "words implied by the context.",
        # The box label prints plural "Examples:" over a single sentence.
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "I went to the library after school, and my mother went "
                    "after work.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of ellipsis. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word ellipsis.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "What is the word omitted in the example sentence?",
            "Rewrite the sentence inserting the omitted word.",
            "Which sentence do you prefer? Why?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using ellipsis.\n"
                            "Hint: Create a sentence involving two people in "
                            "the same situation at different times.\n"
                            "I went to the beach on Saturday, my brother "
                            "went to the beach on Tuesday.\n"
                            "Now omit the second shared word or phrase.\n"
                            "I went to the beach on Saturday, my brother on "
                            "Tuesday.",
             "count": 5},
        ],
    },
    {
        "number": 8,
        "topic": "Antithesis",
        "explanation_label": "Explanation",
        "explanation": "Antithesis is the joining together of two opposing "
                       "ideas.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "My least favorite teacher at my new school is even "
                    "better than my most favorite teacher at my old school.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of antithesis. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word antithesis.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "What is the antithesis in the example sentence?",
            "Rewrite the example sentence as two sentences.",
            "Which way do you like better? Why?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using antithesis.",
             "count": 5},
        ],
    },
    {
        "number": 9,
        "topic": "Diction",
        "explanation_label": "Explanation",
        "explanation": "Writers choose specific words to create style and to "
                       "embellish characters.",
        # Box label "Examples:" — the three contrasted phrases ARE the copy
        # model this week.
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "“It would be my pleasure.” vs. “I’d love to.” vs. “Of "
                    "course, no problem.”",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of diction. (if needed, listen to "
            "the pronunciation on the internet)",
            "Research the history of the word diction.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "Each example is saying the same thing, but how are they "
            "different?",
            # Capital "Thesaurus" and the «"gladly".» period placement are as
            # printed.
            "Use a Thesaurus to find synonyms for “gladly”.",
            "Write the example phrase using the synonyms you found for "
            "gladly.",
        ],
        "practice": [
            # The printed page adds an UNNUMBERED first answer block for the
            # base sentence, then slots 1-5; count stays 5 (the numbered
            # slots) and the instruction carries the base-sentence step.
            {"instruction": "Craft five original sentences using diction.\n"
                            "Begin by writing a simple sentence about a "
                            "topic that interests you. Write the sentence in "
                            "the first set of blank lines. Now, write the "
                            "sentence five different ways using varying "
                            "diction.",
             "count": 5},
        ],
    },
    {
        "number": 10,
        "topic": "Aporia",
        "explanation_label": "Explanation",
        "explanation": "Aporia is a device used to express internal doubt "
                       "about an idea.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "I often wonder what life would truly be like without "
                    "our magnificent bees.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of aporia. (if needed, listen to "
            "the pronunciation on the internet)",
            "Research the history of the word aporia.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "What is being doubted in the example?",
            "Write the sentence as a factual statement by removing the "
            "aporia.",
            "Re-write the sentence, creating a new aporia by adding a new "
            "ending.",
        ],
        "practice": [
            # The hint really ends with a question mark in print.
            {"instruction": "Craft five original sentences using aporia.\n"
                            "Hint: Consider things you wonder about or have "
                            "doubts about?",
             "count": 5},
        ],
    },
    {
        "number": 11,
        "topic": "Eponym",
        "explanation_label": "Explanation",
        "explanation": "Eponyms link the name and attributes of a specific "
                       "person to someone or something else.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "After avoiding her homework and chores for over a week, "
                    "Sophie felt overwhelmed by the Herculean task it would "
                    "be to get caught up.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of eponym. (if needed, listen to "
            "the pronunciation on the internet)",
            "Research the history of the word eponym.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "What is the eponym of the example sentence, what does it mean, "
            "and why is it used?",
            "Rewrite the sentence without using an eponym.",
            "What changes and why?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using eponyms.\n"
                            "Hint: You may need to do some research or ask "
                            "for help.",
             "count": 5},
        ],
    },
    {
        "number": 12,
        "topic": "Distinctio",
        "explanation_label": "Explanation",
        "explanation": "Distinctio elaborates on the meaning of a word "
                       "inside a sentence.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "Little Billy was clever with his homework, and by "
                    "clever, I mean he knew precisely how to talk his mother "
                    "into doing it for him.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of distinctio. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word distinctio.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "Describe the distinctio in the example sentence.",
            "Rewrite the sentence without the distinctio.",
            "How does this affect the sentence?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using distinctio.",
             "count": 5},
        ],
    },
    {
        "number": 13,
        "topic": "Synecdoche",
        "explanation_label": "Explanation",
        "explanation": "Writers use synecdoche to explain a whole by the "
                       "name of one of its parts.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "At sixteen, my sister received her license and the keys "
                    "to her first set of wheels.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of synecdoche. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word synecdoche.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "How is synecdoche used in the example sentence?",
            "Rewrite the sentence without using synecdoche.",
            "Which version do you prefer? Why?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using synecdoche.",
             "count": 5},
        ],
    },
    {
        "number": 14,
        "topic": "Metonymy",
        "explanation_label": "Explanation",
        "explanation": "Metonymy is a device writers use to describe an "
                       "object by using something that’s closely related to "
                       "it.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "After carefully investing his life savings, Tommy paid "
                    "close attention to Wall Street.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of metonymy. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word metonymy.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "What word or phrase in the example sentence is a metonymy?",
            "Rewrite the sentence, communicating the same idea, without "
            "using metonymy.",
            "Which sentence is more effective in communicating the idea? "
            "Why?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using metonymy.",
             "count": 5},
        ],
    },
    {
        "number": 15,
        "topic": "Hypophora",
        "explanation_label": "Explanation",
        "explanation": "Hypophora asks a question, then proceeds to answer "
                       "it immediately.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "Do I ever answer my own questions? Why yes, sometimes "
                    "I do.",
            "citation": "",
        },
        "sentence_two": None,
        "note": "Task 6 really is printed “Which do you prefer? Why?.” — "
                "with a period after the question mark. The stray period is "
                "the guide's typo; a question ends with just the question "
                "mark.",
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of hypophora. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word hypophora.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "Rewrite the example sentence as a single statement without "
            "asking a question.",
            "Which do you prefer? Why?.",
        ],
        "practice": [
            # "thoughts", not "sentences", is as printed this week.
            {"instruction": "Craft five original thoughts using hypophora.",
             "count": 5},
        ],
    },
    {
        "number": 16,
        "topic": "Hyperbaton",
        "explanation_label": "Explanation",
        "explanation": "Hyperbaton arranges words in an unexpected way.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "They will never fail, those who always try their best.",
            "citation": "",
        },
        "sentence_two": None,
        "note": "Task 6 prints “elliminates” — the guide's misspelling of "
                "“eliminates,” kept as printed.",
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of hyperbaton. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word hyperbaton.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "How does the example sentence use hyperbaton?",
            # "elliminates" is as printed.
            "Rewrite the sentence by arranging the words in a way that "
            "elliminates the use of hyperbaton.",
            "Which sentence do you prefer? Why?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using "
                            "hyperbaton.\n"
                            "Begin by crafting a complex sentence.\n"
                            "In springtime the yellow-bellied finches return "
                            "to my garden.\n"
                            "Now rearrange the words.\n"
                            "In springtime return, the yellow-bellied "
                            "finches to my garden.",
             "count": 5},
        ],
    },
    {
        "number": 17,
        "topic": "Polysyndeton",
        "explanation_label": "Explanation",
        "explanation": "Polysyndeton uses conjunctions between each word, "
                       "phrase, or clause.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "I would like to order a Danish, and a donut, and a cup "
                    "of coffee.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of polysyndeton. (if needed, "
            "listen to the pronunciation on the internet)",
            "Research the history of the word polysyndeton.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "Underline the conjunctions in the sentence, then rewrite it "
            "omitting the conjunctions.",
            "Which sentence do you prefer? Why?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using "
                            "polysyndeton.",
             "count": 5},
        ],
    },
    {
        "number": 18,
        "topic": "Metabasis",
        "explanation_label": "Explanation",
        "explanation": "Metabasis sums up information that isn’t explicitly "
                       "in the sentence.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "As you can see from the previous chapter, America as we "
                    "know it would not be the same without the Boston Tea "
                    "Party.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of metabasis. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word metabasis.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "Rewrite the sentence summing up the information with a "
            "different fact.",
            "Rewrite again with yet another fact of summation.",
            "Now choose your favorite sentence and write a new opening to "
            "support the summary information.",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using metabasis.",
             "count": 5},
        ],
    },
    {
        "number": 19,
        "topic": "Cacophony",
        "explanation_label": "Explanation",
        "explanation": "Cacophony describes harsh, discordant sounds.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "The loudspeakers screeched out an evacuation warning as "
                    "sirens wailed on the other side of the walls.",
            "citation": "",
        },
        "sentence_two": None,
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of cacophony. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word cacophony.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "What words or phrases demonstrate cacophony in the example "
            "sentence?",
            "Rewrite the sentence, omitting the cacophony.",
            "Which sentence do you prefer? Why?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using cacophony.",
             "count": 5},
        ],
    },
    {
        "number": 20,
        "topic": "Asterismos",
        "explanation_label": "Explanation",
        "explanation": "Asterismos uses an introductory word or phrase that "
                       "draws attention to what will follow.",
        "example": None,
        "copy_instruction": "Copy the example sentence.",
        "sentence_one": {
            "text": "Okay, class, listen up!",
            "citation": "",
        },
        "sentence_two": None,
        "note": "Task 7 is printed “Now write rewrite the example "
                "sentence…” — the doubled verb is the guide's typo; it means "
                "“Now rewrite….”",
        "questions_two": [],
        "questions_one": [
            "Read and copy the explanation of asterismos. (if needed, listen "
            "to the pronunciation on the internet)",
            "Research the history of the word asterismos.",
            "Read the example sentence silently, then read it again, slowly, "
            "in a whispered tone.",
            "Rewrite the example sentence using a new introductory phrase.",
            "Rewrite the example sentence again using another new "
            "introductory phrase.",
            # "write rewrite" is as printed.
            "Now write rewrite the example sentence without asterismos, from "
            "the perspective of a student telling a friend what the teacher "
            "said.",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using asterismos.",
             "count": 5},
        ],
    },
]


def week_by_number(number):
    return next((w for w in WEEKS if w["number"] == number), None)


def topics():
    return [(w["number"], w["topic"]) for w in WEEKS]
