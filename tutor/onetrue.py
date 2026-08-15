"""One True Sentence, Volume C1: Tools of Style #1 — the guide's content.

Blackbird & Company, by Kimberly Bredberg and Sara Evans. Twenty weeks of
sentence craft: each week introduces one tool of style, shows it working in a
sentence from a Caldecott Award winning book, then asks for five of the
student's own.

Every week has the same shape, so the scaffolding is built once in
seed_onetrue_violet and only the parts that actually differ live here:

    topic            the tool of style this week teaches
    explanation      the guide's own definition of it
    example          an optional worked example with its source
    sentence_one     the model sentence she copies out, and where it is from
    sentence_two     a second sentence, used for the noticing questions
    questions_two    what to notice in sentence two
    questions_one    what to notice in sentence one
    practice         the "Now you try!" groups — usually one group of five,
                     but some weeks split into two groups of three

THE COPYING IS DONE BY HAND. "Copy Sentence 1" is a copywork exercise, and so
is "copy your favourite word or phrase" — see WRITTEN_BY_HAND in the seed.

Transcribed by reading the rendered pages. This PDF has no usable text layer at
all: its own extraction produces things like "?ne True Sentence - Volume Cl" and
loses whole headings, and Violet copies these sentences out by hand.
"""

CURRICULUM_NAME = "One True Sentence: Tools of Style"

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

HOW_IT_TEACHES = """Each week, topics are introduced with an explanation and
example. Students will learn from sentences that demonstrate the topic at hand
crafted by authors of Caldecott Award winning books. As they explore the grammar
and style of each model sentence, they will begin to recognize the elements that
great writers use to construct savvy sentences."""

# The reference section the guide prints for the teacher, kept for the parent
# guide — it is what the weekly lessons quietly assume you know.
BASICS = [
    {
        "part": "Part 1: Four Types of sentences",
        "body": "Declarative sentences state something — fact or opinion or "
                "imagination. Imperative sentences implore or command. "
                "Exclamatory sentences express strong emotion — joy, anger, "
                "sorrow, shock, disbelief. Interrogative sentences always ask, "
                "and end in a question mark.",
        "examples": ["The cat purrs.",
                     "Sassy, the calico cat that we rescued, often falls asleep "
                     "in the sun purring."],
    },
    {
        "part": "Part 2: Words",
        "body": "All sentences are constructed with words. Each word has a "
                "specific meaning and a specific role to play. \"Blare\" as a "
                "verb means to make a very loud, raucous noise; \"blaring\" as "
                "a noun is the noise itself.",
        "examples": ["The alarm clock blared a horrible screeching sound.",
                     "The blaring of the horns during rush hour is exhausting."],
    },
    {
        "part": "Part 3: Phrases",
        "body": "A phrase is a small group of words standing together as a "
                "conceptual unit that is neither the subject nor the predicate, "
                "and never stands alone as a sentence. The five types are noun, "
                "verb, adjective, adverb and prepositional.",
        "examples": ["Skipping stones into the sea, she smiled.",
                     "walk to the blue house · the fish was caught · deep "
                     "menacing blue · sung sweetly · under the rock"],
    },
    {
        "part": "Part 4: Clauses",
        "body": "Every sentence has one. A clause is a group of words that has "
                "both a subject and a predicate. An independent clause makes "
                "sense by itself; a dependent clause does not.",
        "examples": ["The child was happy.",
                     "Because the sun was shining",
                     "Because the sun was shining, the child was happy."],
    },
    {
        "part": "Part 5: Patterns",
        "body": "All sentences fall into five to ten basic subject/predicate "
                "patterns. The subject is what the sentence is about; the "
                "predicate contains the verb or verb phrase, plus any direct or "
                "indirect object.",
        "examples": ["The dog slept.", "The dog chased a cat.",
                     "The dog slept peacefully.", "The dog is called Theo.",
                     "The dog brings the family happiness."],
    },
]

WEEKS = [
    {
        "number": 1,
        "topic": "Imagery",
        "explanation_label": "Explanation",
        "explanation": "Vivid and descriptive (or figurative) language that "
                       "helps readers see pictures in their mind while reading "
                       "is called imagery.",
        "example": {
            "text": "A host, of golden daffodils; / Beside the lake, beneath "
                    "the trees, / Fluttering and dancing in the breeze",
            "citation": "Wordsworth, Daffodils",
        },
        "copy_instruction": "Read and copy Sentence 1.",
        "sentence_one": {
            "text": "Small flowers, white and blue, and violets with golden "
                    "eyes and little waxy white-pink chuckleberry blossoms and "
                    "one tickly smelling pear tree bloomed on the Island.",
            "citation": "Margaret Wise Brown, The Little Island",
        },
        "sentence_two": {
            "text": "The clouds were painted in pastel hues by the departing sun.",
            "citation": "",
        },
        "questions_two": ["Which words or phrases create imagery?"],
        "questions_one": [
            "Based on this week's lesson, how is Sentence 1 similar to Sentence 2?",
            "Where is this week's literary device used in Sentence 1?",
            "Copy your favorite word or phrase from Sentence 1 that helps you "
            "imagine vividly.",
            "How does this word or phrase make Sentence 1 more interesting?",
            "Describe your surroundings with a sentence that uses strong imagery.",
        ],
        "practice": [{"instruction": "Craft five descriptive sentences using rich imagery.", "count": 5}],
    },
    {
        "number": 2,
        "topic": "Capitalization",
        "explanation_label": "Definition",
        "explanation": "Sometimes, there are rules for capitalization. For "
                       "instance, you should always capitalize the first letter "
                       "of a sentence and of a proper noun (specific names, such "
                       "as Ethan, Los Angeles, and Cold Stone Ice Cream). "
                       "However, sometimes authors capitalize certain words just "
                       "to give them more emphasis or to hint that those words "
                       "are very important.",
        "example": None,
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "Instead, he is thinking about other things. Big Things. And "
                    "small things. And sometimes he is thinking about nothing at "
                    "all.",
            "citation": "Dav Pilkey, The Paperboy",
        },
        "sentence_two": {
            "text": "He promised himself he would never feel that sick again as "
                    "he shoved the HALF-EATEN box of double chocolate donuts into "
                    "the trash at his Lake Tahoe cabin.",
            "citation": "",
        },
        "questions_two": [
            "What is a proper noun?",
            "Why are all the letters of “HALF-EATEN” capitalized?",
            "Why is “Lake Tahoe” capitalized?",
        ],
        "questions_one": [
            "Why do you think “Big Things” is capitalized?",
            "What would be different if “Big Things” were not capitalized?",
            "Why do you think “small things” is not capitalized?",
        ],
        "practice": [{"instruction": "Craft five original sentences using as many different types of capitalization as you can.", "count": 5}],
    },
    {
        "number": 3,
        "topic": "You're / Your",
        "explanation_label": "Explanation",
        "explanation": "You're is a contraction (shortened form) of “you are.” "
                       "Your is possessive, showing the subject in the sentence "
                       "owns or is related to something.",
        "example": {
            "text": "You're a doctor.\nWe went to see your doctor.",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "I can't wait to help you in your garden again. We gardeners "
                    "never retire.",
            "citation": "Sarah Stewart, The Gardener",
        },
        "sentence_two": {
            "text": "If you're around a gosling when it first hatches, it will "
                    "imprint on you and follow you wherever you go.",
            "citation": "",
        },
        "questions_two": [
            "Why is “you're” used in this sentence, instead of “your”?",
            "Write out “You're my hero!” without using a contraction.",
            "Complete the following sentences using “your” or “you're.”\n"
            "______ a very good speller.\n"
            "______ dog loves to go on walks.",
        ],
        "questions_one": [
            "In Sentence 1, why is “your” used instead of “you're”?",
            "In Sentence 2, why is “you're” used instead of “your”?",
            "Why do you think it is important to use the correct form of “your” "
            "and “you're”?",
        ],
        "practice": [
            {"instruction": "Craft three original sentences using you're.",
             "count": 3},
            {"instruction": "Craft three original sentences using your.",
             "count": 3},
        ],
    },
    {
        "number": 4,
        "topic": "It's / Its",
        "explanation_label": "Explanation",
        "explanation": "It's is a contraction (shortened form) of “it is.” Its "
                       "is possessive, showing the subject in the sentence owns "
                       "or is related to something.",
        "example": {
            "text": "It's so hot today.\nThe cat was sleepier than its owner.",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "To its line he tied a stronger line, which his friends "
                    "pulled back to their tower.",
            "citation": "Mordecai Gerstein, The Man who walked between the towers",
        },
        "sentence_two": {
            "text": "It's never too late to learn something new.",
            "citation": "",
        },
        "questions_two": [
            "Why is “it's” used in this sentence, instead of “its”?",
            "Write out “it's” three times without using a contraction.",
            "Complete the following sentences using “it's” or “its.”\n"
            "______ color was the brightest orange, ever!\n"
            "______ always enjoyable to have friends over.",
        ],
        "questions_one": [
            "Why is “its” used in Sentence 1 instead of “it's”?",
            "Why is “it's” used in Sentence 2 instead of “its”?",
            "Why do you think it is important to use the correct form of “its” "
            "and “it's”?",
        ],
        "practice": [
            {"instruction": "Craft three original sentences using It's.",
             "count": 3},
            {"instruction": "Craft three original sentences using its.",
             "count": 3},
        ],
    },
    {
        "number": 5,
        "topic": "Prepositional Phrase",
        "explanation_label": "Explanation",
        "explanation": "Prepositions are words such as: at, above, along, "
                       "before, by, for, from, in, of, to, or with, that express "
                       "a relationship to something. A prepositional phrase "
                       "begins with a preposition and ends with a noun. "
                       "Prepositional phrases provide important information "
                       "about people, places, things, relationships, and ideas. "
                       "They also help tell a story. One could simply write, "
                       "“She met him.” but, “She met him at the bridge” tells "
                       "you more about the story.",
        "example": {
            "text": "at the bridge · from Istanbul · of fabric · on the table · "
                    "along the sidewalk",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "He packed a bag of goose feathers that his children had "
                    "collected from the barnyard geese.",
            "citation": "Donald Hall, Ox-Cart Man",
        },
        "sentence_two": {
            "text": "The flags fluttered above the bay, a welcoming wave to "
                    "ships navigating into the harbor.",
            "citation": "",
        },
        "questions_two": [
            "Underline and copy the prepositional phrases in this sentence.",
            "Look for prepositional phrases in other things you have read and "
            "make a list of as many as you can find.",
        ],
        "questions_one": [
            "Where are the prepositional phrases in Sentence 1? Underline and "
            "copy them.",
            "Why are prepositional phrases important?",
            "The author does not have to mention the goose feathers are “from "
            "the barnyard geese,” but he does — what does this add to the "
            "sentence?",
            "Rewrite Sentence 1 adding an original prepositional phrase of your "
            "own after “He packed a bag of goose feathers…”, in order to tell a "
            "different story.\nEXAMPLE: He packed a bag of goose feathers that "
            "he found at the end of the rainbow.",
        ],
        "practice": [
            {"instruction": "Craft five original sentences that each contains a "
                            "prepositional phrase at the beginning, middle, or "
                            "end.",
             "count": 5},
        ],
    },
    {
        "number": 6,
        "topic": "Repetition",
        "explanation_label": "Explanation",
        "explanation": "Using the same word or phrase more than once is called "
                       "repetition. Repetition can be used to emphasize "
                       "something, to make an idea clearer, or to provide a "
                       "sense of rhythm.",
        "example": None,
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "The wild things roared their terrible roars and gnashed "
                    "their terrible teeth and rolled their terrible eyes and "
                    "showed their terrible claws…",
            "citation": "Maurice Sendak, Where The Wild Things Are",
        },
        "sentence_two": {
            "text": "The glittering sunlight danced off the calm waves and "
                    "danced over the warm sand and danced between the palm "
                    "fronds.",
            "citation": "",
        },
        "questions_two": [
            "What literary device from this week's topic is found in this "
            "sentence?",
            "Which word is an example of this literary device?",
        ],
        "questions_one": [
            "Based on this week's lesson, how is Sentence 1 like Sentence 2?",
            "How is this week's device used in Sentence 1?",
            "Why would an author use repetition?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences each containing "
                            "repetition of words or phrases.",
             "count": 5},
        ],
    },
    {
        "number": 7,
        "topic": "They're / Their / There",
        "explanation_label": "Explanation",
        "explanation": "They're is a contraction (shortened form) of “they "
                       "are.” Their is possessive, showing the subject in the "
                       "sentence owns or is related to something. There is used "
                       "to indicate a location or position of something.",
        "example": {
            "text": "They're going to take a bus to the baseball game.\n"
                    "Watching baseball is their favorite thing to do on the "
                    "weekend.\nThe closest bus stop is right over there.",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "Bless the hands that never tire / In their loving care of me.",
            "citation": "Rachel Field, Prayer for a Child",
        },
        "sentence_two": {
            "text": "When plants are kept in the dark confines of shade too "
                    "long, they're sure to wither.",
            "citation": "",
        },
        "questions_two": [
            "Why is “they're” used in this sentence instead of “their” or "
            "“there”?",
            "Fill in the blanks using “their,” “there,” or “they're”.\n"
            "______ going to eat lunch now.\n"
            "______ is my backpack!\n"
            "______ cat has green eyes.",
        ],
        "questions_one": [
            "Why is “their” the right word to use in Sentence 1?",
            "Why is it important to use “they're”, “their” and “there” "
            "correctly?",
        ],
        "practice": [
            {"instruction": "Craft two original sentences using “they're.”",
             "count": 2},
            {"instruction": "Craft two original sentences using “their.”",
             "count": 2},
            {"instruction": "Craft two original sentences using “there.”",
             "count": 2},
        ],
    },
    {
        "number": 8,
        "topic": "Fragment",
        "explanation_label": "Explanation",
        "explanation": "Fragments are incomplete sentences which are usually "
                       "disconnected from the main sentence. Fragments often "
                       "begin with prepositions (like “with,” “of,” or “in”) or "
                       "conjunctions (like “and,” “because,” or “but.”). Authors "
                       "sometimes use fragments on purpose to inject style.",
        "example": {
            "text": "Fragment: “Such as black or blue.”\n"
                    "Complete sentence: “I like darker colors, such as black or "
                    "blue.”",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "And it began to hiss like a snake and roar like a lion.",
            "citation": "William Steig, The Amazing Bone",
        },
        "sentence_two": {
            "text": "In the alley with the cobblestones and stray cats.",
            "citation": "",
        },
        "questions_two": [
            "How can you tell this sentence is a fragment?",
            "What other words can begin fragments?",
        ],
        "questions_one": [
            "What word shows you that Sentence 1 is a fragment?",
            "Fragments are not often used in formal writing. However, sometimes "
            "fragments are used to produce a certain effect or style. Why would "
            "the author choose to use a fragment in Sentence 1?",
        ],
        # This week's practice is paired: a fragment, then the same idea made
        # whole. The seed builds two answers per item.
        "practice": [
            {"instruction": "Craft four fragments, then rewrite each as a "
                            "complete sentence.\nEXAMPLE:\nFragment: Across the "
                            "deep, dark sky.\nSentence: The comet streaked "
                            "across the deep, dark sky.",
             "count": 4, "paired": ("fragment", "sentence")},
        ],
    },
    {
        "number": 9,
        "topic": "Alliteration",
        "explanation_label": "Explanation",
        "explanation": "Using words close to one another that begin with the "
                       "same letter or similar sounds is called alliteration.",
        "example": {
            "text": "Crazy calico cats consuming crispy croissants left copious "
                    "crumbs on my crimson carpet.",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "He packed a shawl his wife wove on a loom from yarn spun at "
                    "the spinning wheel from sheep sheared in April.",
            "citation": "Donald Hall, Ox-Cart Man",
        },
        "sentence_two": {
            "text": "The grass teased and tickled Tom's toes as he traipsed "
                    "across the lawn.",
            "citation": "",
        },
        "questions_two": [
            "What is “alliteration”?",
            "What letter is used for alliteration in Sentence 2?",
        ],
        "questions_one": [
            "What letter is used for alliteration in Sentence 1?",
            "Why would an author use alliteration in a sentence?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences containing "
                            "alliteration.",
             "count": 5},
        ],
    },
    {
        "number": 10,
        "topic": "Conjunction",
        "explanation_label": "Explanation",
        "explanation": "Conjunctions are words that join sentences together.",
        "example": {"text": "and, but, because, if, since, until, or, so",
                    "citation": ""},
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "One morning Momo was more impatient than ever, because the "
                    "sun was brighter than ever.",
            "citation": "Tarō Yashima, Umbrella",
        },
        "sentence_two": {
            "text": "Lady Helen made sure to put the kettle on before her "
                    "esteemed guest arrived, since it would be rude to have the "
                    "Queen over and not serve tea.",
            "citation": "",
        },
        "questions_two": [
            "Which word in this sentence is a conjunction?",
            "What other conjunctions can you name?",
        ],
        "questions_one": [
            "Which word in Sentence 1 is a conjunction?",
            "Why are conjunctions important in a sentence?",
            "How does Sentence 1 use the device of imagery?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences, each having at least "
                            "one conjunction.",
             "count": 5},
        ],
    },
    {
        "number": 11,
        "topic": "Personification",
        "explanation_label": "Explanation",
        "explanation": "Giving an animal or object human characteristics is "
                       "called personification.",
        "example": {
            "text": "The wind whispered.\nThe trees clapped their hands.\nThe "
                    "butterflies had a meeting outside my window.",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "A seal sniffs softly as he recognizes you, and eider ducks "
                    "and fishhawks— all are listening, all are watching as you "
                    "row.",
            "citation": "Robert McCloskey, Time of Wonder",
        },
        "sentence_two": {
            "text": "The golden leaf somersaulted joyfully in the wind as the "
                    "children chased it through the park.",
            "citation": "",
        },
        "questions_two": [
            "How does this sentence use personification? (Think about the words "
            "that are usually applied to humans.)",
            "How can a volcano be personified? Write an original sentence that "
            "personifies a volcano.",
        ],
        "questions_one": ["How does Sentence 1 use personification?"],
        "practice": [
            {"instruction": "Craft five original sentences using personification.",
             "count": 5},
        ],
    },
    {
        "number": 12,
        "topic": "Then / Than",
        "explanation_label": "Explanation",
        "explanation": "Use then to refer to time or sequence. Use than to "
                       "compare two or more things. Usually, a comparison word "
                       "in the sentence will let you know that you need to use "
                       "“than” instead of “then.”",
        "example": {
            "text": "We went to dinner, then we went to the movies.\n"
                    "He is taller than she is. (“Taller” is the comparison word "
                    "in this sentence.)",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "They were delighted with Johnny's bear— he was much bigger "
                    "than they had ever hoped for.”",
            "citation": "Lynd Ward, The Biggest Bear",
        },
        "sentence_two": {
            "text": "Dorothy pridefully thought herself more generous than "
                    "anyone, she then proceeded to snatch the cookie from "
                    "Dorothy's hand and shove it in her own mouth, leaving only "
                    "crumbs.",
            "citation": "",
        },
        "questions_two": [
            "Why is “than” used in the first part of the sentence?",
            "What is the comparison word?",
            "Why is “then” used in the second part?",
        ],
        "questions_one": ["Why is “than” used in Sentence 1?"],
        "practice": [
            {"instruction": "Craft three original sentences using “then” and "
                            "three using “than”.\nAlternate practice: craft "
                            "three original sentences that each use both “then” "
                            "and “than”.",
             "count": 6},
        ],
    },
    {
        "number": 13,
        "topic": "Superlative",
        "explanation_label": "Explanation",
        "explanation": "Superlatives compare two or more things. Superlatives "
                       "usually end with “est” or are preceded by “most” and "
                       "show that something has the most of a certain quality.",
        "example": {"text": "biggest, tallest, most interesting", "citation": ""},
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "The best time of all was when the old swallows taught the "
                    "baby birds to fly.",
            "citation": "Leo Politi, Song of the Swallows",
        },
        "sentence_two": {
            "text": "The most delightful stories to read are riddled with truths "
                    "that speak to the reader and create a relatable world.",
            "citation": "",
        },
        "questions_two": [
            "What is the superlative in this sentence?",
            "Complete the following word lists as in the example of “big”.\n"
            "big, biggest\nhot, ______\ngreen, ______\nfast, ______\n"
            "sad, ______\ndeep, ______",
        ],
        "questions_one": ["Make a list of five more superlatives."],
        "practice": [
            {"instruction": "Craft five original sentences using a superlative "
                            "in each.",
             "count": 5},
        ],
    },
    {
        "number": 14,
        "topic": "Consonance",
        "explanation_label": "Explanation",
        "explanation": "The recurrence of similar consonant sounds in close "
                       "proximity is called consonance. With consonance, the "
                       "similar sounds are found in the middle or at the end of "
                       "the words, unlike alliteration, where similar sounds are "
                       "usually at the beginning.",
        "example": {
            "text": "All's well that ends well.\nI think I would like a drink.",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "The mission was still lovely but there was now a feeling of "
                    "loneliness without the swallows.",
            "citation": "Leo Politi, Song of the Swallows",
        },
        "sentence_two": {
            "text": "The lapping waves could barely reach the creature on the "
                    "beach.",
            "citation": "",
        },
        "questions_two": [
            "Which words demonstrate consonance in Sentence 2?",
            "What is consonance?",
        ],
        "questions_one": [
            "Which words demonstrate consonance in Sentence 1?",
            "Why would an author use consonance?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using consonance.",
             "count": 5},
        ],
    },
    {
        "number": 15,
        "topic": "Metaphor",
        "explanation_label": "Explanation",
        "explanation": "A figure of speech that helps explain an abstract idea "
                       "by making a comparison, without using the words “like” "
                       "or “as,” is called a metaphor.",
        "example": {
            "text": "The bleeding yolk of sunrise filtered color across the "
                    "crisp dawn.",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "But I was a shadow as we walked home.",
            "citation": "Jane Yolen, Owl Moon",
        },
        "sentence_two": {
            "text": "A pillow of seeds from the milkweed settled around the base "
                    "of the pot, ready to take flight.",
            "citation": "",
        },
        "questions_two": [
            "What is a metaphor?",
            "What is being compared in Sentence 2?",
        ],
        "questions_one": [
            "What is being compared in Sentence 1?",
            "Re-write Sentence 1 without using a metaphor.",
            "How does the use of metaphor in Sentence 1 help the author tell the "
            "story?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using metaphor.",
             "count": 5},
        ],
    },
    {
        "number": 16,
        "topic": "Simile",
        "explanation_label": "Explanation",
        "explanation": "Simile is a figure of speech that helps explain an idea "
                       "by making a comparison using the words “like” or “as”.",
        "example": {
            "text": "The bright orange roses looked like flames burning in the "
                    "blossoming bush.",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "Somewhere behind us a train whistle blew, long and low, "
                    "like a sad, sad song.",
            "citation": "Jane Yolen, Owl Moon",
        },
        "sentence_two": {
            "text": "The laughter in the other room sounded like a pack of "
                    "hyenas.",
            "citation": "",
        },
        "questions_two": [
            "What is a simile?",
            "What is being compared in Sentence 2?",
        ],
        "questions_one": [
            "What is being compared in Sentence 1?",
            "Re-write Sentence 1 without using a simile.",
            "How does the use of simile in Sentence 1 help the author tell the "
            "story?",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using simile.",
             "count": 5},
        ],
    },
    {
        "number": 17,
        "topic": "Slang",
        "explanation_label": "Explanation",
        "explanation": "Slang is a very informal word or phrase used in place of "
                       "common language to make it more colorful, and is found "
                       "more often in speech than in writing.",
        "example": {
            "text": "After receiving the sincere apology from his best friend, "
                    "Taylor said, “Don't worry, we're cool.”",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "But he couldn't talk. He had no voice. He was stone drunk.",
            "citation": "William Steig, Sylvester and the Magic Pebble",
        },
        "sentence_two": {
            "text": "The wallflowers at the dance lined themselves up on either "
                    "side of the room.",
            "citation": "",
        },
        "questions_two": [
            "What is slang?",
            "What is the slang word used in Sentence 2?",
        ],
        "questions_one": [
            "What is the slang word used in Sentence 1?",
            "How is slang useful in speech or in a story?",
            "List five slang words you know and their definitions.",
        ],
        "practice": [
            {"instruction": "Craft five original sentences using slang.",
             "count": 5},
        ],
    },
    {
        "number": 18,
        "topic": "To / Too / Two",
        "explanation_label": "Explanation",
        "explanation": "To is an expression of motion or direction. Also used "
                       "with the base form of a verb. Too is a higher degree "
                       "than desirable; in addition; also. Two is quantity and "
                       "expresses the numeral 2.",
        "example": {
            "text": "I am going to the store.\nThere are too many people in this "
                    "room.\nI would like two scoops of ice cream.",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "Except it was no fun to count the pennies alone.",
            "citation": "Sharon Bell Mathis, The Hundred Penny Box",
        },
        "sentence_two": {
            "text": "I need two oars for my boat, one for each hand.",
            "citation": "",
        },
        "questions_two": [
            "Why is “two” used in this sentence instead of “to” or “too”?",
            "Fill in the blanks.\n1. The soup is ______ hot to eat.\n"
            "2. You should get to the airport ______ hours early.\n"
            "3. She was sprinting ______ the finish line.",
        ],
        "questions_one": [
            "Why is “to” used in Sentence 1?",
            "Why is it important to use “to,” “too,” and “two,” correctly?",
        ],
        "practice": [
            {"instruction": "Craft two original sentences using “to”.",
             "count": 2},
            {"instruction": "Craft two original sentences using “too”.",
             "count": 2},
            {"instruction": "Craft two original sentences using “two”.",
             "count": 2},
        ],
    },
    {
        "number": 19,
        "topic": "Run-on",
        "explanation_label": "Explanation",
        "explanation": "A sentence containing two or more independent clauses "
                       "not separated with proper punctuation is called a "
                       "run-on, or run-on sentence. An independent clause is a "
                       "group of words that can stand alone as a sentence. An "
                       "independent clause has both a subject and a verb and "
                       "forms a complete thought.",
        "example": {
            "text": "There once was a butterfly who never wanted to leave the "
                    "sky and he never wanted to land or sleep if it meant he "
                    "wouldn't be flying..",
            "citation": "",
        },
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "When his cart was full, he waved good-bye to his wife, his "
                    "daughter, and his son and he walked at his ox's head ten "
                    "days over hills, through valleys, by streams, past farms "
                    "and villages until he came to Portsmouth and Portsmouth "
                    "Market.",
            "citation": "Donald Hall, Ox-Cart Man",
        },
        "sentence_two": {
            "text": "The candle fell over and lit the bench on fire and then the "
                    "tablecloth caught on fire before I noticed the runaway "
                    "flames.",
            "citation": "",
        },
        "questions_two": [
            "How can you tell Sentence 2 is a run-on?",
            "How can Sentence 2 be corrected so that it is not a run-on?",
        ],
        "questions_one": [
            "How can you tell Sentence 1 is a run-on?",
            "Authors sometimes use run-ons intentionally to produce a certain "
            "effect or style. Why do you think the author chose to make Sentence "
            "1 a run-on?",
            "If Sentence 1 were broken into several sentences, would it have the "
            "same effect? Why or why not?",
        ],
        "practice": [
            {"instruction": "Craft an original run-on sentence (#1), then "
                            "rewrite it with the independent clauses as separate "
                            "sentences (#2).",
             "count": 3, "paired": ("run-on", "rewritten")},
        ],
    },
    {
        "number": 20,
        "topic": "Comparative",
        "explanation_label": "Explanation",
        "explanation": "Comparatives usually end with “-er” or are preceded by "
                       "“more” to show that something has more of a quality than "
                       "something else.",
        "example": {"text": "bigger\nslower\nmore interesting", "citation": ""},
        "copy_instruction": "Copy Sentence 1.",
        "sentence_one": {
            "text": "One day late in summer, Julian noticed that the swallows "
                    "were noisier and more excited than usual.",
            "citation": "Leo Politi, Song of the Swallows",
        },
        "sentence_two": {
            "text": "I feel more rested when I go to bed early instead of "
                    "staying up late.",
            "citation": "",
        },
        "questions_two": [
            "What is the comparative in Sentence 2?",
            "List five comparatives.",
        ],
        "questions_one": [
            "What are the comparatives in Sentence 1? (Hint: there are two.)",
            "Fill in the blanks with the comparative form for each word. Use a "
            "dictionary to help you determine the correct form and spelling.\n"
            "1. bright, ______\n2. small, ______\n3. clean, ______\n"
            "4. good, ______\n5. dry, ______\n6. fun, ______\n7. careful, ______",
        ],
        "practice": [
            {"instruction": "Craft two original sentences using comparatives "
                            "ending in “-er”.",
             "count": 2},
            {"instruction": "Craft two original sentences using comparatives "
                            "with the word “more”.",
             "count": 2},
        ],
    },
]


def week_by_number(number):
    return next((w for w in WEEKS if w["number"] == number), None)


def topics():
    return [(w["number"], w["topic"]) for w in WEEKS]
