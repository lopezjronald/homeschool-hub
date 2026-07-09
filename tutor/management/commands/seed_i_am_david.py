"""Seed Kaylin's Blackbird & Company "I Am David" course (idempotent).

Digitizes the family's purchased Level 7 Literature Discovery Guide for private
use: the five-section structure (Read → Journal → Acquire → Recollect → Explore
→ Glean), every comprehension/discussion question, the vocabulary lists, the
writing prompts, and the guide's grading rubrics — plus authored Socratic
seminar sets in the CenterForLit "Teaching the Classics" story-grammar style
(setting → characters → conflict → plot → theme), grounded in the novel.

Examples:
    python manage.py seed_i_am_david --for-user ronald
    python manage.py seed_i_am_david --for-user ronald --child-name Kaylin
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Curriculum, CurriculumPlacement, CurriculumResource, Lesson
from curricula.services import apply_blueprint, get_blueprint
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet

# ---------------------------------------------------------------------------
# Shared rubric text (verbatim Blackbird points + the guide's writing rubric),
# with a mastery mapping so the AI grader speaks the app's language.
# ---------------------------------------------------------------------------

MASTERY_NOTE = (
    "\n\n> **Mastery mapping:** Accomplished → Mastered · Proficient → Proficient · "
    "Basic → Developing · Limited/Poor → Beginning."
)

JOURNAL_RUBRIC = """## Blackbird grading — Journal (4 points)

Characters **2** · Setting **1** · Plot **1**. Full points for complete, creative work
that goes beyond the basic requirements.

- Notes are **bullet-point phrases**, not essays.
- Characters describe **who a character is** (appearance, personality, background,
  strengths, weaknesses) — not what he does (that belongs in Plot).
- Setting names the **historical time period and geographic location** plus details
  (room, weather, season, time of day).
- Plot gives **simple reminders of major events** — not a retelling.""" + MASTERY_NOTE

ACQUIRE_RUBRIC = """## Blackbird grading — Acquire (2 points)

- All seven words defined **with a dictionary**, in the student's own words.
- Five original sentences that each **illustrate the word's meaning** — a sentence
  that paints a picture, not just "I saw a quay." """ + MASTERY_NOTE

RECOLLECT_RUBRIC = """## Blackbird grading — Recollect (3 points)

- Every question answered in **complete sentences**.
- Answers are **accurate to the book** (the student may refer to the book and
  journal notes; noting page numbers is encouraged).""" + MASTERY_NOTE

WRITING_RUBRIC = """## Blackbird grading — Explore: Writing (4 points)

**Accomplished (4 points)**
- Creatively focuses on the topic
- Uses logical progression of ideas to develop and supports topic with details
- Varies sentence structure
- Uses interesting transitions and strong word choice
- Mature understanding of writing conventions

**Proficient (3 points)**
- Focuses on topic and includes adequate support
- Uses logical progression of ideas to develop and loosely supports topic
- Some varied sentence structure
- Transitions and word choice are adequate but not creative
- General understanding of writing conventions

**Basic (2.5 points)**
- Topic is addressed, but unclear
- Lacks logical progression of ideas and support is weak
- Sentences are stagnant and uninteresting
- Lack of transitions and average word choice
- Partial understanding of writing conventions

**Limited (2 points)**
- Topic may be mentioned, but not clearly addressed and supported loosely
- Organization pattern is weak
- Writing contains sentence fragments and run-on's
- Poor transitions and word choice
- Definite misunderstanding of writing conventions

**Poor (1 point)**
- Topic is not addressed or clearly supported
- Organizational pattern is lacking
- Sentence structure is insufficient
- Non-existent transitions and inappropriate word choice
- Frequent errors in basic writing conventions""" + MASTERY_NOTE

DISCUSSION_RUBRIC = """## Blackbird grading — Explore: Discussion (3 points)

These are springboard questions with **no single right answer**. Credit thoughtful
engagement: opinions **supported with reasons and examples from the book**, honest
personal connections, and willingness to wrestle with hard questions.""" + MASTERY_NOTE

SOCRATIC_RUBRIC = """## Socratic seminar — story-grammar standard (CenterForLit style)

Assess the *quality of thinking*, not agreement with any position:

- **Grounded:** claims point back to scenes, details, or quotes from the novel.
- **Story grammar:** the answer engages the element asked about (setting, character,
  conflict, plot/climax, theme) rather than retelling.
- **Reasoned:** takes a position and defends it; considers the other side.
- **Connected:** links conflict to theme (they are intimately related in this method).""" + MASTERY_NOTE

GLEAN_RUBRIC = """## Blackbird grading — Glean: Final Project (20 points)

Full points for a complete, creative project that goes beyond the basic
requirements: a clear plan, real research or drafting steps, and a finished piece
the student can present and explain.""" + MASTERY_NOTE

VOCAB_HINT = "Look it up in a printed dictionary, then write the definition in your own words."
SENTENCE_PROMPT = (
    "Choose five of your vocabulary words and use each in a complete sentence "
    "that illustrates your understanding of the word's meaning."
)
SENTENCE_HINT = (
    "Make each sentence paint a picture. Not: \"I saw a picture.\" But: \"Whenever I "
    "look at the picture I painted of my dog, it reminds me of how much I love him.\""
)
RECOLLECT_INTRO = (
    "Answer the following questions using complete sentences. You may refer to both "
    "the book and your journal notes. Jot the page number next to your answer when "
    "you can — it makes discussion easier!"
)
JOURNAL_INTRO = (
    "Take notes AS YOU READ — bullet points are perfect. These notes are your "
    "treasure chest for the questions and discussion later in the week."
)
WRITING_INTRO = (
    "Follow the writing process: Brainstorm → Rough Draft → Conference (read it "
    "yourself, then talk to someone about it) → Re-write → Edit → Final Draft. "
    "Your rough draft goes in the first box; your polished final goes in the second."
)
SOCRATIC_INTRO = (
    "Big questions, no single right answer! Think like a detective of stories: "
    "point to scenes and details from the book to back up what you say. It's okay "
    "to change your mind while you write — that means you're thinking."
)

# ---------------------------------------------------------------------------
# The four reading sections. Question tuples are (category, prompt, hint).
# Blackbird questions are verbatim from the family's guide; Socratic sets are
# authored in the CenterForLit story-grammar ladder for this novel.
# ---------------------------------------------------------------------------

SECTIONS = [
    {  # ------------------------------------------------------- Section 1
        "number": 1,
        "chapters": "Chapters 1–2",
        "characters": "David · The Man · Johannes",
        "vocab": ["catastrophe", "grating", "irresolute", "lithe", "mutter", "quay", "runnel"],
        "recollect": [
            "What instructions does the man give to David?",
            "What article does David request from the man?",
            "What has David desired to do since he was little?",
            "What does David realize after reaching the thicket?",
            "What memory enters David's mind while riding in the back of the truck?",
            "While on the boat, what does David realize that causes him to be filled with loneliness?",
            "By the end of chapter one, what does David desire?",
            "As David prepares himself to interact with people, what does he realize he must have?",
            "When David assesses his situation, what advantages and disadvantages does he think he has?",
            "What belief grows stronger for David with the passing of time?",
        ],
        "writing_prompt": (
            "Imagine you have a friend who has never been outside or seen anything but a "
            "grey room. Write a paragraph describing one of the following things to him: "
            "the ocean, the sky, a mountain, a meadow, a tree, or your favorite animal. "
            "Since the person has never seen anything, describing what it looks like will "
            "not be very helpful. You will have to think about how something sounds, how "
            "it smells, what it feels like, how it makes you feel, and maybe even how it "
            "tastes."
        ),
        "discussion": [
            ("character", "Why do you think David doesn't call the man by name?"),
            ("application", "Why do you think the man is helping David escape? Would you put yourself in danger to help someone? Why or why not?"),
            ("character", "Why do you think David does not trust people? Have you ever been in a situation where you have not trusted someone? Describe your experience."),
            ("theme", "Why do you think the prisoners don't allow themselves to think?"),
            ("character", "Why do you think the memory of Johannes is so strong in David's mind, and why does he try not to think of him?"),
            ("theme", "Why do you think washing is so important to David? What do you think David might be trying to rid himself of besides dirt?"),
            ("style", "Why do you think David is so strongly impacted by the color around him? How does color impact you?"),
            ("theme", "Why does David think it is important to always do what one thinks is right? How can someone know what is right? What if you think something is wrong that someone else thinks is right? What will you do?"),
            ("plot", "What conclusion does David come to about the people in the town? What do you think about his conclusion?"),
        ],
        "socratic": [
            ("context",
             "Before the story begins, David has spent his whole life in a prison camp behind the Iron Curtain. What do you know — or what can you find out — about why governments in Eastern Europe imprisoned people at this time?",
             "Think Cold War: some governments imprisoned people simply for disagreeing with them. The map at the end of your guide shows the Iron Curtain line."),
            ("setting",
             "The story opens inside the camp at night, then bursts into the open countryside. How does Anne Holm make the two places FEEL different? Find one detail of each.",
             "Compare what David sees, hears, and fears inside the wire with what overwhelms him outside — colors, the sea, the sky."),
            ("character",
             "What does David know how to do incredibly well because of the camp — and what ordinary things does he not know at all? What does that contrast tell you about him?",
             "He can survive, stay silent, read danger… but what about smiling, playing, being a kid?"),
            ("character",
             "The man who helps David is never named. What do you think the man wants — and why might the author keep him a mystery?",
             "Great mysteries make readers ask questions. What changes for YOU because you don't know his reasons yet?"),
            ("conflict",
             "CenterForLit calls I Am David a story of Man vs. Man and Man vs. Society. In these chapters, though, David's hardest battles seem to happen inside him. What is David's biggest struggle so far — 'them,' the world, or himself? Defend your answer.",
             "There's no wrong pick — but you must give evidence. Where does fear come from in chapter 1?"),
            ("plot",
             "What is the single most important decision anyone makes in these chapters? What would the story become if it had gone the other way?",
             "Is it the man's decision… or David's moment at the fence… or something quieter?"),
            ("theme",
             "David is out of the camp — but is he FREE? What would have to change for David to be truly free?",
             "Think about what he carries with him: fear, distrust, the habit of not thinking."),
            ("theme",
             "David concludes that people cannot be trusted and that one must never get caught. Where did that belief come from — and do you predict the story will prove him right or wrong?",
             "Keep this answer! You'll want to look back at it in Section 4."),
        ],
    },
    {  # ------------------------------------------------------- Section 2
        "number": 2,
        "chapters": "Chapters 3–4",
        "characters": "David · Johannes · Carlo · Maria",
        "vocab": ["brevity", "disconcert", "ignorant", "inundate", "muster", "sinister", "undulate"],
        "recollect": [
            "What important article does David lose?",
            "What god does David choose and how does he choose?",
            "When David meets the man and woman on the road, why does he want to know if the country they come from has a king?",
            "What observation does the woman make about David?",
            "What two reasons does David have for wanting to find a mirror?",
            "What could David no longer think of giving up?",
            "What two things does David ask God for?",
            "In chapter 4, what strange new sound does David hear?",
            "When David is being attacked by Carlo, why doesn't he defend himself?",
            "What does David realize he is doing for the first time after he rescues Maria?",
        ],
        "writing_prompt": (
            "Imagine you have to choose a god to believe in, what characteristics would "
            "be important to you?"
        ),
        "discussion": [
            ("theme", "Johannes once said, \"Greedy people can never be happy,\" he also said, \"When you very much want something you haven't got, you no longer care for what you have got.\" Do you agree with these statements? Why or why not? Can you give examples to support your opinion?"),
            ("context", "When David is trying to decide about his belief in God, he remembers what another David said about his God—\"He maketh me to lie down in green pastures: He leadeth me beside the still waters.\" Why do you think this quote impacted David so strongly? Where can the quote that David remembers be found?"),
            ("conflict", "Why does David fear questions from strangers? Do you think his fear is justified? Why or why not?"),
            ("character", "What conclusion does David come to about the truck driver Angelo, and what is he surprised to discover?"),
            ("character", "When Maria awakens after David rescues her from the fire, the first thing she asks David is his name. How is this different from the questions people usually asked David? Why do you think this impacted David so strongly?"),
            ("theme", "Why does David think it is always important to say thank you? What is your opinion and why?"),
            ("conflict", "Why is David torn between wanting to stay with the family and wanting to leave?"),
        ],
        "socratic": [
            ("setting",
             "David crosses into Italy — sunshine, markets, churches, families. Pick one scene where the setting nearly overwhelms David. Why does beauty hit him so hard?",
             "Someone who has only known grey sees color for the first time. Find the actual moment on the page."),
            ("character",
             "David chooses a God — the God of the green pastures and still waters. What does his WAY of choosing (careful, reasoned, cautious) tell you about who he is?",
             "Most people inherit a faith. David interviews one. What kind of mind does that?"),
            ("character",
             "Maria's first question to David is his NAME — not his papers, not where he's from. Why does that undo him? What has David never had before?",
             "To be asked your name is to be treated as a person, not a problem."),
            ("conflict",
             "When Carlo attacks him, David refuses to fight back. Is that weakness, strength, or something else entirely? What is David really refusing to become?",
             "Remember where David learned what violence does to people."),
            ("conflict",
             "Man vs. Society: checkpoints, papers, suspicious adults, questions. Where do you see the world itself pressing against David in these chapters — even when no one means him harm?",
             "Fear of questions is fear of a system. Which moments show it?"),
            ("plot",
             "David runs into the burning shed to save Maria. Some readers call this the first moment David acts like a FREE person. Do you agree — is this a turning point in the plot? Why?",
             "A turning point changes what's possible afterward. What becomes possible for David after the fire?"),
            ("theme",
             "Sacrificial love: David risks the only thing he has — his freedom — for a stranger. What is this story starting to say about what love costs?",
             "Who else has paid a price for David so far? Keep a list; it will grow."),
            ("theme",
             "David smiles for the first time. Why does the author make something so small feel so enormous?",
             "What has to be true inside a person before a real smile can happen?"),
        ],
    },
    {  # ------------------------------------------------------- Section 3
        "number": 3,
        "chapters": "Chapters 5–6",
        "characters": "The Man · Johannes · Maria · Signora Hartman",
        "vocab": ["deception", "emaciated", "foreboding", "fugitive", "indebted", "ingratiate", "obstinate"],
        "recollect": [
            "What is David learning about language and the use of words?",
            "Why does David ask for a book that was published before 1917?",
            "What does David decide about Carlo and why?",
            "Which of the children does David feel most at ease with, and why do you think this is so?",
            "What does David think sounds more wonderful than anything in the world except sunshine and beauty?",
            "What does the milk cause David to remember and how does this affect his opinion of \"the man\" in the camp?",
            "What revelation does the priest give David regarding David's God?",
            "What offer does the Priest make to David and what does David ask for instead?",
            "What does David realize has changed about himself since he has lived in a house with a family?",
            "What can David no longer do that was essential for his survival in a concentration camp?",
        ],
        "writing_prompt": "Describe in detail what you think is the most wonderful thing in the world.",
        "discussion": [
            ("application", "What do you think about David's refusal to play certain games? Think of a situation like this that you might experience and explain why you would or would not act as David did."),
            ("character", "Why do you think David does not like to be touched?"),
            ("theme", "What is the difference between admiration and devotion?"),
            ("character", "What does David's letter to Maria and Carlo's parents tell you about his character?"),
            ("character", "How does Maria's mother try to ease her conscience regarding David?"),
            ("theme", "What do you think about David's observation, \"The way you spoke was a reflection of how you thought.\"? Do you agree? Why or why not?"),
            ("theme", "What does David believe is needed to go on living, and how does he break that \"need\" with Maria? Do you agree with his belief?"),
            ("plot", "What revelations does Signora Hartman make regarding the photograph, and what effect do you think these revelations will have on David?"),
            ("character", "What doesn't David understand about the children?"),
            ("character", "How do the father's and mother's opinion of David differ?"),
        ],
        "socratic": [
            ("setting",
             "Living inside a family's home is a brand-new country for David — with its own strange laws. Which rules of family life confuse him most, and why?",
             "Games, touch, jokes, being given things without paying… what does each mix-up reveal?"),
            ("character",
             "David asks for a book printed before 1917. Think about what happened in Russia in 1917 — what does this request tell you about how carefully David thinks, and what he fears?",
             "1917 = the Russian Revolution. Why would David distrust books printed after it?"),
            ("character",
             "David writes a letter to Maria and Carlo's parents before leaving. What does the letter say that David could never say out loud — and why is writing easier for him?",
             "Some truths need distance. What does that tell you about wounds and words?"),
            ("conflict",
             "Man vs. Self: David discovers comfort has softened him — he can no longer stay camp-alert. Is comfort a friend or an enemy in this story? Make your case.",
             "What did alertness cost him? What does softness give him? Can he have both?"),
            ("plot",
             "The priest tells David his God is real and can be asked for help. How does this scene change David's journey from running-AWAY-from into traveling-TOWARD?",
             "A fugitive flees; a pilgrim seeks. Which is David becoming?"),
            ("plot",
             "Signora Hartman's photograph changes everything. Some readers say the true climax of the whole book begins here. What do YOU think is the story's climax so far? Argue for your candidate.",
             "CenterForLit tip: the climax connects the main character's deepest motivation to the resolution of the biggest conflict. What does David want most?"),
            ("theme",
             "\"The way you spoke was a reflection of how you thought.\" What is the novel saying about words — and where do David's careful, old-fashioned words come from?",
             "Johannes taught him. What else did Johannes plant in David that is only now blooming?"),
            ("theme",
             "Faith, hope, and trust: David begins to let people in — a little. Which character has earned his trust the most, and what exactly did it take?",
             "Trust is expensive for David. List the payments."),
            ("application",
             "David cannot play games where losing feels dangerous. What does his struggle teach about what childhood play is FOR?",
             "Play is practice at failing safely. What happens to a person who never got to practice?"),
        ],
    },
    {  # ------------------------------------------------------- Section 4
        "number": 4,
        "chapters": "Chapters 7–8",
        "characters": "David · Johannes · King",
        "vocab": ["apathy", "apprehensive", "gale", "precipice", "shirk", "vagabond", "dejected"],
        "recollect": [
            "How had the man helped David in the camp?",
            "How do David and King become friends and who makes the first move toward friendship?",
            "Why does the farmer try to hide the fact that spring is coming?",
            "Why does David become angry with God and what lesson does he realize God is trying to teach him?",
            "How does King protect David and how does this affect David?",
            "What does David frequently have to do that makes him uncomfortable?",
            "What should David have noticed about the three people he met on the road?",
            "In David's prayer to God, what does he ask for?",
            "After blaming himself for King's fate, what does David come to realize?",
            "What does David realize as soon as the door of the woman's house is opened?",
        ],
        "writing_prompt": (
            "Describe how you might be feeling if you were about to see someone you had "
            "waited your whole life to meet."
        ),
        "discussion": [
            ("application", "David talks about being torn between two things, like wanting to be awake and wanting to sleep at the same time. Describe a time when you have felt torn between two things. How did you choose between the two?"),
            ("character", "How are the farmer's children different from Maria, Andrea and Carlo?"),
            ("character", "How do you think David's experience with the farmer's children affected his opinion of Carlo?"),
            ("theme", "David lies to many people in order to keep them from becoming suspicious about him. Do you think it was wrong for David to lie? Do you think it is always wrong to lie?"),
            ("theme", "What do you think are some lessons David learned from King?"),
            ("style", "What do you think is meant by the phrase, \"...the woman whose eyes had seen so much and yet could smile\"?"),
            ("plot", "What is significant about how David's mother greets him?"),
        ],
        "socratic": [
            ("setting",
             "Winter on the mountain farm nearly stops David's journey cold. How does Anne Holm use weather and seasons to mirror what is happening inside David?",
             "When is the world frozen? When does it thaw? Track David's heart alongside."),
            ("character",
             "King the dog gives David something no human has managed to give him yet. What is it — and why could a dog get past defenses that kept every person out?",
             "A dog asks no questions, checks no papers, wants no story."),
            ("conflict",
             "David becomes angry at God — a real argument. What is that argument actually about? And how is arguing WITH someone different from having no one at all?",
             "You only argue with someone you believe is there. What does the fight prove?"),
            ("plot",
             "King's sacrifice lets David escape. The story has now shown sacrifice from the man, from David (for Maria), and from King. Why does the author keep returning to this one idea?",
             "Reading Roadmaps names 'sacrificial love' as this book's great theme. Trace the chain: who pays for whom?"),
            ("plot",
             "The climax debate, final round: what is THE climax of I Am David — the escape, the fire, the photograph, King's sacrifice, or the door opening in Denmark? Make your case with evidence.",
             "The climax ties David's deepest motivation to the resolution of the story's biggest conflict. What was David really searching for all along?"),
            ("theme",
             "\"I am David.\" The book ends with the words it is named for. Why do these three small words carry the whole story? What does David finally HAVE when he says them?",
             "Compare: who could David say he was in chapter 1? A number? A nobody? What changed?"),
            ("theme",
             "Determination: what kept David walking all the way to Denmark — fear, hope, or the mother he didn't know he had? Did his reason CHANGE during the journey?",
             "Look at why he started running vs. why he finished."),
            ("style",
             "\"...the woman whose eyes had seen so much and yet could smile.\" Holm tells us almost nothing and suggests everything. How does this restraint make the ending MORE powerful, not less?",
             "What do you imagine her eyes have seen? The author trusts you to fill it in — that trust is the technique."),
            ("application",
             "David's journey runs from 'no one' to 'someone' — a name, a face, a mother, a home. What does this story say to anyone who has ever felt invisible?",
             "Answer for David first. Then, if you're willing, answer for you."),
        ],
    },
]

# Novel-grounded LITERARY ELEMENT questions added to each section's Socratic set —
# the "parts of literature" layer (symbol, foreshadowing, irony, motif, POV, genre).
LITERARY_ELEMENTS = {
    1: [
        ("style",
         "SYMBOL — the very first thing David asks the man for is a bar of SOAP, and washing "
         "becomes almost sacred to him. Beyond getting clean, what do you think the washing stands for?",
         "He's scrubbing away more than dirt. What does 'clean' mean to someone leaving a camp?"),
        ("style",
         "SYMBOL — the compass points David south toward freedom. How does the author use the compass "
         "to stand for David's whole journey — and why does it matter later when he loses it?",
         "A compass gives direction and hope. What happens to hope when the compass is gone?"),
    ],
    2: [
        ("style",
         "COLOR & LIGHT — after the grey camp, Holm floods Italy with color and sunshine. How is COLOR "
         "used as a symbol here? Find a moment where it nearly overwhelms David.",
         "Grey stood for the camp and death; color stands for life. Track where color bursts in."),
        ("style",
         "FORESHADOWING — David's first real SMILE comes when he saves Maria. How does the author make "
         "such a tiny moment feel enormous, and what does it hint about who David is becoming?",
         "A first smile is a promise. What does it foreshadow about the rest of the journey?"),
    ],
    3: [
        ("style",
         "SYMBOL — Signora Hartman's PHOTOGRAPH turns the whole story. Why is a photograph the perfect "
         "object to do that? What does it hold and point toward?",
         "A photo holds the past and points to the future. Whose face is about to matter most?"),
        ("style",
         "IRONY — David, who trusts no one, is safest among strangers, yet a 'kind' farmer will later "
         "betray him. How does the author use irony about trust and kindness?",
         "Irony = the opposite of what you'd expect. Who turns out trustworthy, and who doesn't?"),
    ],
    4: [
        ("style",
         "MOTIF & TITLE — the book ends with the very words it is named for: 'I am David.' Why title the "
         "whole story after these three words? Trace how the idea of his NAME returns from chapter 1 to the end.",
         "A motif is an idea that keeps coming back. In chapter 1 he was almost a number; at the end?"),
        ("theme",
         "POINT OF VIEW — we see everything through David's eyes alone. How would the story change if we "
         "saw it through his mother's eyes, or the farmer's? Why did Holm keep us inside David?",
         "Limited POV keeps secrets (like his mother) until David learns them. Why is that powerful?"),
        ("style",
         "GENRE — is this an adventure, a survival story, or something deeper? What clues tell you what "
         "KIND of story it really is?",
         "Genre shapes what you expect. Is the true journey outside David, or inside him?"),
    ],
}

# Blackbird & Company answer key (from the publisher's teacher key) — grader
# reference for the comprehension sets; never shown to the student.
ANSWER_KEYS = {
    1: """## Comprehension answer key — Section 1 (Chapters 1–2)
1. Wait for the signal, take a compass heading south to Salonika, board a boat to Italy, and hide.
2. A piece of soap.
3. To be free — to escape his captors and the man who controls him.
4. That no gunfire followed his escape (no one is chasing him yet).
5. Johannes suddenly collapsing and dying in the back of the truck.
6. Realizing Johannes is not with him — he is completely alone.
7. Seeing natural beauty, he no longer wants capture or death; he wants to LIVE.
8. A story he can stick to when people question him.
9. Advantages: strength, sharp senses, survival skills, languages. Disadvantages: he doesn't know geography, which foods are safe, and — worst of all — people.
10. His belief that he will eventually get away grows stronger.""",
    2: """## Comprehension answer key — Section 2 (Chapters 3–4)
1. His compass (his most precious possession) — dropped into the sea.
2. "The God of the green pastures and still waters" (Johannes's God); he chooses carefully, by reasoning.
3. To learn whether the country is free (has a king rather than "them").
4. That he is no ordinary little boy — his eyes and manner are unusual.
5. To see what is wrong with his eyes, and to change/check his appearance.
6. His freedom — after living free he can no longer imagine giving it up.
7. To take away his fear for a while, and to send a good man driving the truck.
8. Music (for the first time).
9. Because fighting back would make him as worthless as his captors — unworthy of freedom.
10. Smiling — for the first time, out of happiness.""",
    3: """## Comprehension answer key — Section 3 (Chapters 5–6)
1. That words have different qualities; a bigger vocabulary lets him think and communicate better.
2. To be sure it is truthful — printed before "they" (the Soviets) could fill it with propaganda (pre-1917).
3. That Carlo is bad, because he is skilled at hiding his true intentions.
4. Maria — she senses his discomfort, never makes him feel ignorant, and values his thoughts.
5. Going to school — he wants it almost as much as sunshine and beauty.
6. The camp milk/vitamins; he realizes the man in the camp actually helped him, though he questions his motives.
7. That they share the same God — the God of the church David entered.
8. A map — he asks instead to see where Italy is and where Switzerland begins.
9. He is no longer perfectly content; life outdoors alone has lost its appeal after living with a family.
10. He can no longer detach his emotions (essential for camp survival) now that the family has reached his heart.""",
    4: """## Comprehension answer key — Section 4 (Chapters 7–8)
1. He gave David milk and vitamins and made sure Johannes looked after him.
2. King (the dog) approaches, sniffs him, and lies beside him; the dog makes the first move.
3. To keep David as free labor — hiding that spring (and David's promised release) has come.
4. That he has not forgiven Carlo, who kept apologizing; he must let his own anger go.
5. King defends David from the farmer; David is so moved that he cries.
6. Lying to people — it troubles him deeply because he wants to be honest.
7. That they had the dejected, dull-eyed look of camp prisoners (they were dangerous).
8. First a painless death; then, remembering King, he asks God to take care of him.
9. That King chose freely to follow and protect him — it was the dog's own nature.
10. That he recognizes the woman from a photograph — she is his mother.""",
}


GLEAN_OPTIONS = """Choose ONE (or more!) of the guide's final projects:

1. **Epilogue** — What might David's life be like after the story? Write an epilogue set one, five, or ten years after David is reunited with his mother.
2. **Alternate ending** — What if David had NOT found his mother at the end? Write a new ending (2–4 pages) with this scenario in mind.
3. **One different choice** — Describe how you would have acted differently in one particular situation and how that might have changed the outcome of the story.
4. **Research essay** — Many countries still imprison people unfairly today. Research a real situation, describe it, and explain what is being done — and what YOU could do — to help.
5. **Map of the journey** — Using the guide's map of Cold War Europe: label the countries, locate where the prison camp may have been, trace David's route with as many labeled places as possible, and research one location.
6. **Essay** — Choose the most thought-provoking discussion question in this guide and answer it in essay form, starting from an outline and working through the full writing process."""


class Command(BaseCommand):
    help = "Seed the Blackbird 'I Am David' course + Socratic seminars for a child (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--for-user", required=True, help="Username who owns the curriculum.")
        parser.add_argument("--child-name", default="Kaylin", help="Child to place in the course.")

    @transaction.atomic
    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(username=options["for_user"])
        except User.DoesNotExist:
            raise CommandError(f"User '{options['for_user']}' does not exist.")

        blueprint = get_blueprint("blackbird_i_am_david")
        family = get_active_family(user)
        curriculum, created = Curriculum.objects.get_or_create(
            parent=user,
            name=blueprint["name"],
            defaults={
                "subject": blueprint["subject"],
                "grade_level": blueprint["grade_level"],
                "family": family,
            },
        )
        chapters, lessons = apply_blueprint(curriculum, blueprint)
        self.stdout.write(
            f"{'Created' if created else 'Using'} curriculum #{curriculum.pk} "
            f"({chapters} sections, {lessons} lessons)."
        )

        # Place the child at Section 1: Read (never resets existing progress).
        child = Student.objects.filter(
            parent=user, first_name__iexact=options["child_name"],
        ).first()
        if child is None:
            raise CommandError(f"No child named '{options['child_name']}' found for {user.username}.")
        first_lesson = Lesson.objects.get(
            chapter__curriculum=curriculum, chapter__number=1, order=1,
        )
        _, placed = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum, defaults={"current_lesson": first_lesson},
        )

        set_count = q_count = 0
        for section in SECTIONS:
            n, chs = section["number"], section["chapters"]
            journal = self._lesson(curriculum, n, 2)
            acquire = self._lesson(curriculum, n, 3)
            recollect = self._lesson(curriculum, n, 4)
            explore = self._lesson(curriculum, n, 5)

            # -- Journal ---------------------------------------------------
            s, q = self._seed_set(
                journal, family,
                title=f"Section {n} · Journal",
                reading=chs,
                intro=JOURNAL_INTRO,
                rubric=JOURNAL_RUBRIC,
                questions=[
                    ("character",
                     "CHARACTERS — as you read, note interesting, important, and new things "
                     "about each person below: their personality and appearance, and details "
                     "about the way they act, think, and feel.",
                     "Bullet points are perfect! Describe who each character IS — not what they do (save that for Plot).",
                     {"response_type": Question.TYPE_CHARACTERS, "passage": section["characters"]}),
                    ("setting",
                     "SETTING — as you read, note where the story is happening. Explain how "
                     "the setting is significant to the story and include any descriptive "
                     "details you find.",
                     "Time period, country, weather, season, time of day — and why the place matters."),
                    ("plot",
                     "PLOT — summarize what happens in this section of the story.",
                     "Major events only — simple reminders, not a retelling."),
                ],
            )
            set_count += s; q_count += q

            # -- Acquire ---------------------------------------------------
            vocab_questions = [
                ("vocabulary", f"Define: **{word}**", VOCAB_HINT)
                for word in section["vocab"]
            ]
            vocab_questions.append(("application", SENTENCE_PROMPT, SENTENCE_HINT))
            s, q = self._seed_set(
                acquire, family,
                title=f"Section {n} · Vocabulary",
                reading=chs,
                intro="Use a real dictionary — the paper kind! Define each word in your own words.",
                rubric=ACQUIRE_RUBRIC,
                questions=vocab_questions,
            )
            set_count += s; q_count += q

            # -- Recollect (answer key grounds the grader) ------------------
            s, q = self._seed_set(
                recollect, family,
                title=f"Section {n} · Comprehension",
                reading=chs,
                intro=RECOLLECT_INTRO,
                rubric=RECOLLECT_RUBRIC,
                questions=[("comprehension", prompt, "") for prompt in section["recollect"]],
                answer_key=ANSWER_KEYS.get(n, ""),
            )
            set_count += s; q_count += q

            # -- Explore: Writing -------------------------------------------
            s, q = self._seed_set(
                explore, family,
                title=f"Section {n} · Writing Exercise",
                reading=chs,
                intro=WRITING_INTRO,
                rubric=WRITING_RUBRIC,
                questions=[
                    ("application",
                     f"ROUGH DRAFT — Write a complete paragraph based on this topic. Remember "
                     f"to include a topic sentence, several supporting sentences, and a "
                     f"concluding sentence.\n\n“{section['writing_prompt']}”",
                     "Just get your thoughts on paper — the polish comes next."),
                    ("application",
                     "FINAL DRAFT — Thoroughly edit your rough draft, make any necessary "
                     "changes, then write your final version here.",
                     "Check spelling, grammar, punctuation — and read it out loud to hear the flow."),
                ],
            )
            set_count += s; q_count += q

            # -- Explore: Discussion (Blackbird's own questions) — teacher-led
            s, q = self._seed_set(
                explore, family,
                title=f"Section {n} · Discussion",
                reading=chs,
                intro="Lead these aloud with your student — no writing required. Springboard "
                      "questions with no single right answer; press for reasons and examples "
                      "from the book.",
                rubric=DISCUSSION_RUBRIC,
                questions=[(cat, prompt, "") for cat, prompt in section["discussion"]],
                mode=QuestionSet.MODE_DISCUSSION,
            )
            set_count += s; q_count += q

            # -- Socratic seminar: novel-grounded story grammar + literary elements
            s, q = self._seed_set(
                explore, family,
                title=f"Section {n} · Socratic Seminar",
                reading=chs,
                intro=SOCRATIC_INTRO,
                rubric=SOCRATIC_RUBRIC,
                questions=section["socratic"] + LITERARY_ELEMENTS.get(n, []),
                mode=QuestionSet.MODE_DISCUSSION,
            )
            set_count += s; q_count += q

        # -- Whole-book literature standard: Socratic Story-Grammar Seminar +
        #    the grade-level Literary Toolbox (reusable framework, one call).
        from tutor import literature

        # Remove the earlier inline seminar location if a prior run created it.
        QuestionSet.objects.filter(
            lesson__chapter__curriculum=curriculum,
            title="Whole-Book · Story-Grammar Seminar",
        ).delete()
        s, q = literature.apply_literature_standard(curriculum, child.grade_level, family=family)
        set_count += s; q_count += q

        # -- Glean ----------------------------------------------------------
        glean = self._lesson(curriculum, 5, 1)
        s, q = self._seed_set(
            glean, family,
            title="Section 5 · Glean: Final Project",
            reading="",
            intro=GLEAN_OPTIONS,
            rubric=GLEAN_RUBRIC,
            questions=[
                ("application",
                 "Which project option (1–6) did you choose — and why does it fit you?",
                 "Pick the one you'd be excited to show someone."),
                ("application",
                 "Make your plan: list the steps, the materials you need, and what 'finished' will look like.",
                 "A good plan has at least 4 steps and a finish line."),
                ("application",
                 "When your project is done: reflect here. What did the project teach you about the story that the weekly work didn't?",
                 "Also: what are you proudest of?"),
            ],
        )
        set_count += s; q_count += q

        # Teacher-reference answer-key link (never shown to the student).
        CurriculumResource.objects.get_or_create(
            curriculum=curriculum,
            url="https://blackbirdandcompany.com/information-for-parents-and-teachers/answer-keys/i-am-david/",
            defaults={
                "label": "Blackbird Answer Key",
                "resource_type": CurriculumResource.ANSWER_KEY,
                "teacher_only": True,
                "order": 0,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {set_count} question sets, {q_count} questions. "
            f"{child.first_name} placed at {'Section 1: Read' if placed else 'existing progress (kept)'}."
        ))

    # -- helpers -------------------------------------------------------------

    def _lesson(self, curriculum, chapter_number, order):
        return Lesson.objects.get(
            chapter__curriculum=curriculum, chapter__number=chapter_number, order=order,
        )

    def _seed_set(self, lesson, family, *, title, reading, intro, rubric, questions,
                  mode=QuestionSet.MODE_STUDENT, answer_key=""):
        qset, _ = QuestionSet.objects.update_or_create(
            lesson=lesson,
            title=title,
            defaults={
                "family": family,
                "intro": intro,
                "reading": reading,
                "rubric": rubric,
                "answer_key": answer_key,
                "status": QuestionSet.APPROVED,
                "mode": mode,
            },
        )
        count = 0
        for i, item in enumerate(questions, start=1):
            # Each question is (category, prompt, hint) with an optional 4th
            # element: a dict of extra Question fields (response_type, passage).
            category, prompt, hint = item[0], item[1], item[2]
            extra = item[3] if len(item) > 3 else {}
            Question.objects.update_or_create(
                question_set=qset,
                order=i,
                defaults={
                    "category": category, "prompt": prompt, "hint": hint,
                    "response_type": extra.get("response_type", Question.TYPE_TEXT),
                    "passage": extra.get("passage", ""),
                },
            )
            count += 1
        # Drop stale questions beyond the current list — but never delete one a
        # child has already answered (that would orphan their saved response).
        stale = qset.questions.filter(order__gt=len(questions))
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {
                int(k) for k, v in (sheet.answers or {}).items() if str(v).strip() and k.isdigit()
            }
        stale.exclude(pk__in=answered).delete()
        return 1, count
