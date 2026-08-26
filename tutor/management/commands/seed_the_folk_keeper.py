"""Seed Kaylin's Blackbird "The Folk Keeper" course (idempotent).

Follows the family's purchased Blackbird & Company Literature & Writing Discovery
Guide (Level 3, used at grade 7) for private family use: the five-week shape
(Read → Journal → Acquire → Recollect → Explore, then Glean), the guide's own
uneven section divisions (chapters 1-4, 5-8, 9-11, 12-16), its vocabulary,
comprehension questions, writing exercises and discussion questions. Teacher
answer keys ride on each set's ``answer_key`` (never shown to the student) and
come from the publisher's own online key; the official key is also linked as a
teacher-only CurriculumResource.

Joyce leads this one with Kaylin, and the guide is discussion-heavy by design:
every section carries the guide's own Discussion questions plus the app's
Socratic story-grammar seminar, both oral (MODE_DISCUSSION) — nothing to type.

Two writing prompts (Sections 1 and 2) and part of a third are set in a
decorative font that did not survive text extraction from the PDF; they are
reconstructed from the legible fragments and flagged below. Check them against
the printed workbook before Kaylin writes to them.

Run:  python manage.py seed_the_folk_keeper --for-user ronald
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from curricula.models import Curriculum, CurriculumPlacement, CurriculumResource, Lesson
from curricula.services import apply_blueprint, get_blueprint
from core.utils import get_active_family
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet


MASTERY_NOTE = (
    "\n\nAssess mastery, not perfection — Beginning · Developing · Proficient · "
    "Mastered. Reward complete, thoughtful work that reaches past the minimum."
)

JOURNAL_RUBRIC = """## Blackbird grading — Journal (4 points: Characters 2 · Setting 1 · Plot 1)
Section weights (20 pts): Read 4 · Journal 4 · Acquire 2 · Recollect 3 · Explore 7
(Writing 4, Discussion 3). Award the Read points for completing the section's reading.
- Characters: notes describe who a character IS (appearance, personality, how they act, think and feel).
- Setting: where and when — and why the place matters. Cliffsend is not scenery; the Folk draw their strength from it.
- Plot: the major events in order — reminders, not a retelling.
- Bullet points are perfect.""" + MASTERY_NOTE

ACQUIRE_RUBRIC = """## Blackbird grading — Acquire (2 points)
Definitions in the child's OWN words, from a printed dictionary, plus five original
sentences that show the meaning rather than repeat the definition. The publisher's
definitions are in the key below for your reference only.""" + MASTERY_NOTE

RECOLLECT_RUBRIC = """## Blackbird grading — Recollect (3 points)
Complete sentences, drawn from the book and the journal notes. The publisher's answer
key is below (teacher reference only — never shown to the student). Accept answers that
capture the key idea in the child's own words.""" + MASTERY_NOTE

WRITING_RUBRIC = """## Blackbird grading — Explore: Writing (4 points)
- **Accomplished (4)** — creatively focused; logical progression with supporting details; varied sentences; strong word choice; mature conventions.
- **Proficient (3)** — focused with adequate support; mostly logical; some sentence variety; general command of conventions.
- **Basic (2.5)** — topic addressed but unclear; weak support and progression; average word choice; partial command of conventions.
- **Limited (2)** — topic barely addressed; weak organization; fragments and run-ons; poor transitions.
Billingsley writes with a rich, specific lexicon; reward Kaylin for reaching for the exact word.""" + MASTERY_NOTE

DISCUSSION_RUBRIC = """## Blackbird grading — Explore: Discussion (3 points)
Assess the quality of thinking, not agreement: reasons grounded in the story, and a
willingness to explain. These are springboards — there is no single right answer.""" + MASTERY_NOTE

SOCRATIC_RUBRIC = """## Socratic seminar — story-grammar standard (CenterForLit style)
Grounded (points back to the page), reasoned (gives a because), and connected (links
conflict to theme). This is oral — celebrate thinking out loud. Corinna is an unreliable
narrator about herself; the best moments come when Kaylin notices the gap between what
Corinna says she is and what she does.""" + MASTERY_NOTE

GLEAN_RUBRIC = """## Blackbird grading — Glean: Final Project (20 points)
One or more of the guide's assignment options, taken through the full writing process
where writing is involved. Assess effort, completeness and creativity.""" + MASTERY_NOTE

VOCAB_HINT = "Look it up in a printed dictionary, then write the definition in your own words."

# The guide gives five NUMBERED lines for the sentence task, so it seeds as five
# separate questions — one input box each — rather than one box to cram five
# sentences into. Each sentence is then gradeable on its own, the way the printed
# page reads. This is the house pattern for Blackbird vocabulary from here on;
# I Am David keeps its single box because Kaylin already has work saved in it.
SENTENCE_COUNT = 5
SENTENCE_PROMPT = (
    "**Sentence {i} of {n}** — choose one of your vocabulary words (a different one "
    "each time) and use it in a complete sentence that illustrates your understanding "
    "of the word's meaning."
)
SENTENCE_HINT = (
    "A sentence that shows the meaning beats one that just repeats the definition. "
    "Underline or capitalize the vocabulary word so it's easy to spot."
)

RECOLLECT_INTRO = (
    "Answer the following questions using complete sentences. You may refer to both "
    "the book and your Journal notes."
)
JOURNAL_INTRO = (
    "As you read, keep a reading journal. For each character below, jot bullet-point "
    "notes about WHO they are — what they look like, how they act, think, and feel — "
    "not just what they do (that goes under Plot). Then note the Setting and the main "
    "events of the Plot."
)
WRITING_INTRO = (
    "Write a complete paragraph based on the topic below. Remember to include a topic "
    "sentence, several supporting sentences, and a concluding sentence."
)
DISCUSSION_INTRO = (
    "Think about and discuss the following questions aloud together — no writing "
    "required. Press for reasons and examples from the book."
)
SOCRATIC_INTRO = (
    "A Socratic story-grammar seminar — lead these aloud. Walk the elements: context, "
    "setting, characters, conflict, plot, and theme. Keep pressing back to the book "
    "for evidence."
)


OFFICIAL_DEFINITIONS = {
    "drudgery": "hard, menial, or dull work",
    "ebb": "the movement of the tide to sea",
    "entreated": "asked someone earnestly or anxiously to do something",
    "indulge": "allow oneself to enjoy the pleasure of something",
    "prodigious": "remarkably or impressively great in extent, size or degree",
    "tawdry": "showy but cheap and of poor quality",
    "futile": "pointless, serving no useful purpose",
    "malice": "the intention to cause pain, injury or distress to another",
    "nimble": "quick and light in movement, action or thought",
    "oust": "drive out or expel someone from a position or place",
    "tether": "to tie an animal with a rope or chain so as to restrict its movement",
    "wraith": "a ghost or ghostlike image of someone",
    "crescendo": "a gradual increase in loudness in a piece of music",
    "implacable": "unable to be placated",
    "languorous": "the state or feeling, often pleasant, of tiredness or inertia",
    "lustrous": "having shine",
    "obliged": "legally or morally bound to an action or course of action",
    "tranquil": "free from disturbance; calm",
    "complacent": "showing smug or uncritical satisfaction with oneself or one's achievements",
    "gauze": "a thin translucent fabric of silk, linen, or cotton",
    "inexplicable": "unable to be explained or accounted for",
    "inextricable": "impossible to disentangle or separate",
    "linger": "to stay in place longer than is necessary, typically because of a reluctance to leave",
    "savor": "to taste and enjoy completely",
}


SECTIONS = [
    {  # ------------------------------------------------------- Section 1
        "number": 1,
        "chapters": "Chapters 1–4",
        "characters": "Corinna · Lady Alicia · Sir Edward · Finian",
        "vocab": ["drudgery", "ebb", "entreated", "indulge", "prodigious", "tawdry"],
        "recollect": [
            "Where is Corinna the queen of the world?",
            "What will be Corinna's last act for the Folk of the Rhysbridge Foundling Home?",
            "Why does Corinna not speak her anger?",
            "What secret of Corinna's does Lord Merton know?",
            "What does every rhyme that comes to Corinna have right where the heartbeat should be?",
            "What does Corinna let Sir Edward and Lady Alicia assume?",
            "Why can no one, not even a Folk Keeper, see the Folk?",
            "Where are there no Sealfolk?",
            "What does a good Folk Keeper know all about?",
            "Why does Corinna want, “… to know people's secret passions”?",
            "Where must the Folk of Cliffsend draw terrific strength from?",
            "Why is Corinna able to climb the tree in the shelter of the wall when running from the Hill Hounds?",
            "Corinna would have found the Cellar on her own if she had known to follow what?",
            "What does Corinna feel almost sorry she hasn't the time for?",
        ],
        "writing_prompt": (
            "Corinna describes her world with vivid details and a rich lexicon. Write a paragraph "
            "describing a place you experienced for the first time, recounting the moment in the same "
            "rich detail."
        ),
        "discussion": [
            ("character",
             "Corinna compares herself and her job as Folk Keeper to a lightning rod, and to lightning "
             "itself. How would you describe yourself? What would you compare yourself to?"
            ),
            ("theme",
             "Corinna says, “There is power in silence.” What do you think she means by this? Do you "
             "agree with her? Why or why not?"
            ),
            ("character",
             "Why do you think Corinna says, “… you must never give your anger away”? Why is this "
             "important to her? Do you agree? Why or why not?"
            ),
            ("style",
             "What do you think it means to “trip over an idea”?"
            ),
            ("theme",
             "Consider Corinna's advice: “Vengeance. It is not always as delicious as you anticipate, "
             "but you must not flinch from it. Otherwise the Matrons of the world would rule us all.” "
             "What does she mean by this? Do you agree with her? Why or why not? Do you think it is "
             "good advice? Why or why not?"
            ),
            ("character",
             "How are Corinna and Finian different? How are they the same?"
            ),
            ("character",
             "When Corinna says she has no tears, Finian offers her some of his, saying he “has "
             "plenty.” What do you think he means by this? What does he have to be sad about?"
            ),
            ("application",
             "Corinna transformed her identity and has kept a large secret for years in order to "
             "survive and give herself power. What do you think you would have done in her place?"
            ),
        ],
        "socratic": [
            ("context",
             "Before we talk about Corinna, let's get our bearings in her world. What is a Folk "
             "Keeper, and what do the people in this book believe would happen if nobody did that job?",
             "Think about what the Folk are blamed for — milk, animals, the luck of a household — and "
             "where the Folk are kept. What does it cost a person to be the one who goes down there?"
            ),
            ("setting",
             "Corinna moves from the Rhysbridge Foundling Home to Marblehaugh Park on Cliffsend. How "
             "are those two places different, and what does the book tell us about why the Folk of "
             "Cliffsend are more dangerous than the ones she's used to?",
             "Look for what she says about the Cellar and the stone. If the Folk draw strength from "
             "their home, what kind of home is a rocky island?"
            ),
            ("character",
             "The last thing Corinna does before leaving Rhysbridge is steal Matron's breakfast "
             "sausage. What does that one small act tell us about the kind of person she is?",
             "Was she hungry, or was she saying something? Think about who Matron has been to her and "
             "what stealing lets Corinna keep for herself."
            ),
            ("character",
             "Corinna keeps several secrets — that she is a girl living as 'Corin,' that her hair "
             "grows two inches every night, that she always knows the exact time without a clock. Why "
             "do you think she guards each one so carefully? Point to a moment that shows what she's "
             "afraid of losing.",
             "Ask what a girl in this world is allowed to do, and what a Folk Keeper is allowed to do. "
             "Which secret keeps her fed and housed, and which one she can't explain even to herself?"
            ),
            ("conflict",
             "Lady Alicia and Sir Edward assume Corin had a proper Folk Keeper apprenticeship. Lord "
             "Merton, though, seems to know her secrets before she ever arrives. How does that "
             "difference set up trouble for her?",
             "Count who knows what. If the only person who understands her is the one who is dying, "
             "where does that leave her when he's gone?"
            ),
            ("plot",
             "Walk me through the Hill Hounds chase. What happens, what does Corinna do, and what does "
             "that scene show us that her words about herself don't?",
             "Look at the stunted tree and what she does when she's cornered — and notice whether she "
             "panics, bargains, or holds still. Does she ask anyone for help?"
            ),
            ("theme",
             "Corinna says 'there is power in silence' and 'you must never give your anger away.' What "
             "does she think she gains by staying quiet and holding onto her anger — and can you find "
             "a place in these chapters where it costs her something too?",
             "Try the boat with Finian, or the way she answers Lady Alicia and Sir Edward. If anger is "
             "a thing she saves up, what is she saving it for? And what does she notice missing from "
             "her own rhymes?"
            ),
            ("application",
             "Corinna believes she'll be safest if nobody knows the true things about her. Do you "
             "think that will hold up? Make a prediction we can check later — and tell me about a time "
             "you kept something to yourself because telling felt too risky.",
             "Think about Finian, who already looks at her closely, and about how many secrets one "
             "person can carry at once. Write your prediction down so we can come back to it at the "
             "end of the book."
            ),
        ],
    },
    {  # ------------------------------------------------------- Section 2
        "number": 2,
        "chapters": "Chapters 5–8",
        "characters": "Corinna · Lady Alicia · Sir Edward · Finian",
        "vocab": ["futile", "malice", "nimble", "oust", "tether", "wraith"],
        "recollect": [
            "What do the Folk not have, and what do they not care for?",
            "What is perhaps the first true thing that Corinna tells Lady Alicia?",
            "Who is Lady Rona?",
            "Who is the only one to see Corinna slip off to the Cellar with hundreds of pins stuck in her clothes?",
            "According to Corinna, when do the Folk grow fierce in the Northern Isles?",
            "Why does Corinna leave her Folk Bag in the Cellar?",
            "What does Corinna show Finian that she can coax?",
            "When and where was Corinna given the name Stonewall?",
            "Who is buried under the headstone under the church eaves?",
            "What is Corinna not protected from while in the Cellar inside her triple-layered protection?",
            "What should Corinna have known never to reveal?",
            "When does Old Francis disappear?",
            "Why are the May Day garlands scattered in a circle around the Manor?",
            "What does Finian dress up as for the Masquerade Ball?",
        ],
        "writing_prompt": (
            "Write a paragraph describing a conviction you hold that will help you when something "
            "difficult comes your way — and explain where that conviction came from."
        ),
        "discussion": [
            ("theme",
             "Have you ever heard the phrase, “Kill them with kindness”? This means, when someone "
             "mistreats you, if you can repay them with kind words and actions, you may be able to "
             "kill their anger and soften them. Why doesn't this help combat the Folk?"
            ),
            ("character",
             "Corinna says she likes “the rain and mist” as opposed to “bright skies and bushels of "
             "glaring sunshine.” Why do you think this is? What kind of weather do you prefer and why?"
            ),
            ("application",
             "Corinna observes that Lady Alicia loves Finian most and states, “… anyone could see "
             "that.” If love can be seen by people's actions, how do you see it in the people around "
             "you?"
            ),
            ("style",
             "What do you think Corinna means when she says, “Finian could see more without his "
             "spectacles than most people could who needed none”?"
            ),
            ("theme",
             "Corinna believes promises are “inconvenient.” Why do you think she believes this? Do you "
             "agree with her? Why or why not? Have you ever made a promise that felt inconvenient?"
            ),
            ("character",
             "Finian says Corinna is stubborn and fails to see and experience things that are right in "
             "front of her. Have you ever known someone like this? Have you ever been this way? What "
             "can stubbornness cause us to miss out on?"
            ),
            ("context",
             "At the foundling home, Corinna was not given the opportunity to learn to read and write. "
             "Because of this, she refused to do her chores. Why was she not allowed to learn? What "
             "would you have done in her situation?"
            ),
            ("character",
             "When Corinna walks away from the party on Midsummer's Eve, she feels “… a lump of "
             "desolation.” What do you think causes this? Have you ever felt this way?"
            ),
        ],
        "socratic": [
            ("context",
             "In these chapters Corinna tells us plainly what the Folk are like — that they have no "
             "hearts and that kindness means nothing to them. If kindness doesn't work on them, what "
             "does? Point to a place where she shows us how she really handles them.",
             "Think about what she carries down to the Cellar and what she leaves for them. If a "
             "creature can't be charmed or thanked, a Folk Keeper has to bargain in some other "
             "language — what is that language?"
            ),
            ("setting",
             "Time on Cliffsend gets marked by weather and by customs — the Storms of the Equinox at "
             "one end of this section, May Day garlands ringing the Manor at the other. What has "
             "changed in Corinna's world between those two moments? How do you know?",
             "Compare where she spends her hours early on versus later — the Cellar, the cliffs, the "
             "Windcuffer. Notice who she is spending them with, too."
            ),
            ("character",
             "Corinna finally tells us how she got the name Stonewall — a matron gave it to her "
             "because she was stubborn and refused to boil the soiled linens. What does that story "
             "tell you about the kind of person she has decided to be?",
             "She could have obeyed and been given an easier name. Ask what she was willing to pay to "
             "say no — and whether she still pays that same price at Marblehaugh Park."
            ),
            ("character",
             "When Corinna tells Lady Alicia that she likes the rain, she counts it as the first true "
             "thing she has ever told her. Why would such a small, harmless truth be so hard for her "
             "to say?",
             "Think about what a truth costs someone who is hiding almost everything. If you have one "
             "secret, what happens to a little true thing that slips out near it?"
            ),
            ("conflict",
             "Corinna's whole life depends on nobody knowing who she really is. In this section, who "
             "or what comes closest to catching her out, and what exactly did they see?",
             "Don't only look at the people. There is a dog named Taffy, and there is a night Corinna "
             "slips down to the Cellar bristling with pins. What would that look like to anyone "
             "watching?"
            ),
            ("plot",
             "Several strange things pile up one after another: the dogs tear Sir Edward's trophy skin "
             "to pieces, Old Francis disappears, and Corinna learns that Lady Rona was Lord Merton's "
             "first wife with a child buried under the church eaves. Which two of those feel most "
             "connected to each other, and what makes you link them?",
             "Try laying them out in order on your fingers. Ask who benefits, who is frightened, and "
             "who nobody seems to be looking for — the author put these close together on purpose."
            ),
            ("theme",
             "Corinna guards everything — her anger, her secrets, even her true opinions. Yet out on "
             "the Windcuffer she coaxes the wind into Finian's sails, and she lets him see her do it. "
             "What does she seem to believe happens to a person who gives a piece of herself away?",
             "Two of her own lines are worth holding up here: that promises are inconvenient, and the "
             "lump of desolation she carries afterward. Ask what she gains on that boat and what she "
             "feels she has lost."
            ),
            ("application",
             "At the Masquerade Ball everyone puts on a costume for one night, and Finian comes as a "
             "Cliffsend fisherman — but Corinna wears a costume every single day. Who do you think "
             "will be the first person to see straight through hers, and what do you think will "
             "finally give her away? Let's write your guess down so we can check it when we finish the "
             "book.",
             "Look back at who has already noticed something odd about her and hasn't said so. And you "
             "might ask yourself: is there anything true about you that would feel scary to say out "
             "loud, the way the rain did for her?"
            ),
        ],
    },
    {  # ------------------------------------------------------- Section 3
        "number": 3,
        "chapters": "Chapters 9–11",
        "characters": "Corinna · Lady Alicia · Sir Edward · Finian",
        "vocab": ["crescendo", "implacable", "languorous", "lustrous", "obliged", "tranquil"],
        "recollect": [
            "Who must always leap over the bonfire first?",
            "What does it feel like to hold a brick of warm peat to your breast?",
            "Who says they will never marry?",
            "What joy does Corinna feel when she dives underwater to save Finian?",
            "Why does Corinna sink below the surface of the water when another hand reaches for her?",
            "What is it like when Corinna's feet are sure and light up the cliff path?",
            "What does Corinna believe Finian would laugh at if he knew?",
            "What does Corinna coax Finian to do?",
            "What happens in the ocean after Corinna drips her blood into it?",
            "When a wave smashes Corinna into the mast of the Windcuffer, what does she realize about the water lapping about her ankles?",
            "According to Corinna, when can you not call the Sealfolk?",
            "Everyone thinks breathing in is so important, but what does no one think about?",
            "When does Corinna's mother go mad and refuse to ever again look at the sea?",
            "Sir Edward has hunted long enough to be able to tell what?",
        ],
        "writing_prompt": (
            "When Corinna discovers she is a Sealmaiden, she feels she finally knows who she truly is "
            "and where she belongs. Write a paragraph about a time you learned something about "
            "yourself that changed how you saw your own place in the world."
        ),
        "discussion": [
            ("application",
             "Corinna says she would rather be a Folk Keeper if she could not run an estate like Sir "
             "Edward. Why do you think she says this? If you could pick a position to have from the "
             "story, what would it be, and why?"
            ),
            ("application",
             "After Corinna makes a pact with the sea, she immediately regrets it. Describe a time you "
             "did something you immediately regretted."
            ),
            ("theme",
             "Sir Edward tells Corinna to never reveal to her enemy what is precious to her. Is this "
             "good advice? Why or why not? Is it useful to Corinna? Why or why not?"
            ),
            ("application",
             "Corinna decides to walk through the dark Caverns knowing her Sealskin waits for her on "
             "the other side. When is a time you had to do something scary or unknown in order to "
             "accomplish something? Was it worth it? Why or why not? What helped you to move forward?"
            ),
            ("theme",
             "Corinna says, “I refuse to be trapped inside my fear of the next moonless, starless "
             "night.” How do you think she will accomplish this? Do you think it is possible to refuse "
             "to be fearful? Why or why not?"
            ),
            ("character",
             "Corinna states she will not die as Corinna the Folk Keeper but as Corinna the "
             "Sealmaiden. Why does she want this? How do you think she will accomplish this?"
            ),
            ("style",
             "What do you think Corinna means when she says, “The air is always shifting, boiling "
             "around you, full of mysterious and wonderful things to see — if you only know how to "
             "see”? How would you describe this idea? What is something you “know how to see”?"
            ),
        ],
        "socratic": [
            ("context",
             "This part opens on Midsummer Eve, and the Folk Keeper has to be the first one to leap "
             "the bonfire. Why do you think the islanders give that job to the Folk Keeper instead of "
             "to a lord or a farmer? What does the crowd seem to believe that leap will do?",
             "Think about what the Folk Keeper does the rest of the year, and who has to face the Folk "
             "so nobody else does. Notice how the people act while she waits to jump."
            ),
            ("setting",
             "Corinna carries a warm peat brick against her chest that night. Describe what a "
             "Midsummer bonfire on Cliffsend feels like in this chapter -- the fire, the crowd, the "
             "sea nearby. How does the author make the night feel like a night when strange things are "
             "allowed to happen?",
             "Go back and find two or three details she gives us with her senses: heat, smell, sound, "
             "dark water at the edge of the firelight. Ask what feels ordinary and what feels charged."
            ),
            ("character",
             "When Corinna dives to save Finian, she says she is born again under the water -- she "
             "doesn't need air, her ears close, she feels weightless and joyful. What does that scene "
             "show us about who Corinna really is, and how is the girl in the water different from the "
             "girl on the cliff?",
             "Read the underwater sentences out loud again. Look at the words she uses for how it "
             "feels, then compare them to how she usually talks about her life at Marblehaugh Park."
            ),
            ("character",
             "A hand reaches down for her in the water and she lets herself sink instead of taking it. "
             "Why would a girl choose to sink? What does that refusal tell us about how she feels "
             "toward being helped or being held onto?",
             "Remember how she's survived before now -- who has she ever let take care of her? Also "
             "ask what she is losing if she comes up too soon."
            ),
            ("conflict",
             "Corinna drips her own blood into the ocean, and the sea darkens into a terrible storm. "
             "Is the trouble in this section coming from outside her or from inside her? Point to what "
             "happens right after the blood hits the water to back up your answer.",
             "Line up what she does with what the water does. Then ask whether she seems surprised by "
             "the storm, or whether some part of her expected it."
            ),
            ("plot",
             "A lot of small clues pile up in these chapters: her feet know the cliff path as if she'd "
             "memorized it, there's red hair inside her peat brick, the Windcuffer springs a leak. "
             "Which of these bothers you most, and what do you think the author is quietly building "
             "toward?",
             "Ask yourself which clues are about Corinna's body and which are about someone doing "
             "damage on purpose. Those might be two different mysteries."
            ),
            ("theme",
             "Corinna says, \"I refuse to be trapped inside my fear.\" In this same section we learn her "
             "mother went mad when Lord Merton burned her sealskin, and we're told how much it matters "
             "to breathe out. What is the author saying about fear, and about the difference between "
             "being trapped by something and giving something up?",
             "Notice that breathing out is the thing that lets you go deeper -- you have to let the "
             "air go. Then ask what Corinna's mother lost, and whether she chose to lose it."
            ),
            ("application",
             "Corinna announces she will never marry, and she says it flatly, like a door closing. "
             "What do you think she's really protecting herself from? And here's one to test later: do "
             "you predict she'll keep that promise by the end of the book, or break it -- and what "
             "would have to happen to her to change her mind?",
             "Think about everyone she's ever depended on and how that turned out. Write your "
             "prediction down somewhere so we can come back to it when we finish."
            ),
        ],
    },
    {  # ------------------------------------------------------- Section 4
        "number": 4,
        "chapters": "Chapters 12–16",
        "characters": "Corinna · Lady Alicia · Sir Edward · Finian",
        "vocab": ["complacent", "gauze", "inexplicable", "inextricable", "linger", "savor"],
        "recollect": [
            "The Folk did not frighten Corinna as much as what?",
            "What does Corinna understand when she is alone with her own friendly heartbeat, with her hair long and loose?",
            "What does Corinna realize at once when she emerges from the Cellar?",
            "How is Corinna transformed from savage to servant?",
            "What does Corinna linger over at the stonecutter's tray?",
            "Who pulls Corinna away from the crowd and down an alley at the Harvest Fair?",
            "When Corinna and Finian first met, what did Finian know about Corinna by the way she carried herself?",
            "What does Finian say Corinna could come back from the sea for?",
            "What color are the strands in Finian's peat on Midsummer's Eve?",
            "What have Finian and Lady Alicia gone to Rhysbridge to do?",
            "What could Corinna not do, even for Finian?",
            "What marks Taffy's grave?",
            "The direction of what is built into Corinna's bones?",
            "When Corinna's Sealskin is peeling away from her, why is she thankful she has her words?",
        ],
        "writing_prompt": (
            "Imagine you are keeping a journal like Corinna. Write an entry chronicling a day from "
            "the past. Be sure to include details about important events, and your thoughts on them "
            "as well. Write as if you are living the day all over again."
        ),
        "discussion": [
            ("theme",
             "Corinna says, “There is a price you pay for power.” What does she mean? Do you agree "
             "with her? Why or why not? Can you think of any examples where this is true?"
            ),
            ("style",
             "When Corinna feels herself beginning to cry, she says of water that “It is "
             "accommodating, yet relentless, changing its shape to follow its true path.” What "
             "literary device is she using? In what other ways is this true of water? Can you think of "
             "another way to describe water?"
            ),
            ("character",
             "Corinna shows loyalty towards Finian and Lady Alicia by deciding to wait to turn into a "
             "Sealmaiden until she has warned them about Sir Edward. Do you think she would have done "
             "this if she had discovered she was a Sealmaiden at the beginning of the story? Why or "
             "why not? When is a time you have been loyal to a friend, or a friend has been loyal to "
             "you?"
            ),
            ("application",
             "Do you think it's possible to be worried and relieved at the same time? Why or why not? "
             "If you can, describe a time when this has happened to you."
            ),
            ("conflict",
             "Consider the passage, “Even for Finian, I could not confine myself to land. My heart was "
             "with him, my heart was with the sea, and I knew which I would choose.” Why is this "
             "decision so hard for Corinna? Why is the pull of the sea so strong?"
            ),
            ("theme",
             "Words are very powerful tools. They allow us to interpret and describe the world around "
             "us. In what ways are words powerful or significant in the novel? What are some ways "
             "words are powerful in your life?"
            ),
            ("plot",
             "As Finian runs to where the sealfolk have left Corinna on the beach, she says she knows "
             "what conviction she will give him. What do you think it is?"
            ),
            ("application",
             "What do you think Corinna's life will be like now without her sealskin? What will it be "
             "like without being a Folk Keeper? Will she change? Why or why not?"
            ),
            ("character",
             "Has Finian changed over the course of the novel? Why or why not? If so, how? Was this "
             "change for the better?"
            ),
        ],
        "socratic": [
            ("context",
             "When Corinna comes up out of the Cellar in this section, the whole Manor is empty — "
             "everyone has gone to the Harvest Fair. What does the author gain by emptying the house "
             "right at this moment, and what does Corinna do with all that empty space?",
             "Think about what she can do when nobody is watching her that she couldn't do with a "
             "house full of people. Where does she go, and what does she borrow?"
            ),
            ("setting",
             "Down alone in the dark, Corinna says the Folk frighten her less than she frightens "
             "herself, and that she can carve words from air and float them in a sea of rhyme so that "
             "she always has the last word. What kind of place is the Cellar for her by now — a "
             "prison, a workshop, or something else? Point to the lines that make you say so.",
             "Ask yourself who she is really wrestling with down there. If the Folk aren't the "
             "scariest thing anymore, what is — and why can she stand it better with words?"
            ),
            ("character",
             "Soap and a borrowed set of servant's clothes turn her, in her own words, from savage to "
             "servant. What does that tell you about how Corinna thinks a person becomes somebody — "
             "and is she right?",
             "Count up how many different people she has been so far just by changing what's on the "
             "outside. Does the changing outside ever change the inside too?"
            ),
            ("character",
             "Finian pulls her down an alley at the Harvest Fair and tells her he knew from the very "
             "first that she was no boy — and later she finds silver strands of her own hair worked "
             "into his peat brick. What kind of person is Finian, based on what he did with what he "
             "knew?",
             "He held a secret that could have wrecked her, for a long time. Ask what he did with it — "
             "and what the hair in the peat says about how long he has been paying attention."
            ),
            ("conflict",
             "Finian tells her she could come back from the sea — for the Folk, for him, to marry him "
             "— and yet she finds she cannot confine herself to land even for him. What exactly is "
             "pulling against what inside her here, and how do you know it's a real tug and not an "
             "easy choice?",
             "Look for the places where she admits what she wants and what she can't do at the same "
             "time. If it were easy, would she have hesitated at all?"
            ),
            ("plot",
             "Corinna doesn't just leave — she chooses to warn them first, and Finian and Lady Alicia "
             "go to Rhysbridge to testify about the true heir, which is what finally exposes Sir "
             "Edward. Walk me through how those pieces fall in order. Which one couldn't have happened "
             "without the one before it?",
             "Start with her decision to warn them and follow the chain. Ask what would have happened "
             "to Marblehaugh Park if she had simply gone to the sea without saying a word."
            ),
            ("theme",
             "At the end the sealskin peels away, and Corinna says she is thankful for her words. She "
             "has also marked Taffy's grave with amber beads and can feel the direction of Seal Rock "
             "built into her bones. Of everything she has — the skin, the bones' knowing, the words — "
             "which one does the book seem to say is most truly hers, and why?",
             "Notice which things can be burned, stolen, or hidden by somebody else, and which one "
             "nobody has ever been able to take from her. The beads on the grave are a clue about what "
             "she chooses to give away."
            ),
            ("application",
             "Now think back across the whole book — the shorn hair at Rhysbridge, the Cellar at "
             "Marblehaugh, the sea, and this ending. Corinna spent the whole story hoarding her anger "
             "and her secrets because she believed you must never give anything away, and by the end "
             "she has given away quite a lot. Was she made weaker or stronger by giving? And is there "
             "something you hold on to tightly that you'd be braver for loosening your grip on — let's "
             "check back on that in a month.",
             "Line up an early Corinna moment beside a late one and compare what she is willing to "
             "hand over. If giving cost her something real and she chose it anyway, what does that say "
             "about strength?"
            ),
        ],
    },
]


ANSWER_KEYS = {
    1: """## Comprehension answer key — Section 1 (Chapters 1–4)
1. In the Cellar, where the Folk reside, Corinna is queen of the world.
2. Corinna's last act for the Folk of the Rhysbridge Foundling Home is to steal Matron's breakfast sausage.
3. Corinna does not speak her anger because you must never give your anger away.
4. Lord Merton knows Corinna's secret that she is a girl and that she always knows the time.
5. Every rhyme that comes to Corinna has a hole in its middle where the heartbeat should be.
6. Corinna lets Sir Edward and Lady Alicia assume that she had a proper apprenticeship in the Foundling Home, but in reality she had bribed some lads to teach her to read and write.
7. No one, not even a Folk Keeper, can see the Folk because they cannot bear the light.
8. There are no Sealfolk on the mainland.
9. A good Folk Keeper knows all about charms.
10. Corinna wants "to know people's secret passions" because then you have power over them if needed.
11. The Folk of Cliffsend draw terrific strength from their stony home.
12. Corinna is able to climb the tree when running from the Hill Hounds because it is growing in the shelter of a wall and is thin and stunted.
13. If Corinna had known to follow the smell of baking bread she would have found the Cellar by herself, as it was just outside the kitchens.
14. Corinna is most sorry that she doesn't have time to go sailing with Finian.""",
    2: """## Comprehension answer key — Section 2 (Chapters 5–8)
1. The Folk do not have hearts and do not care for kindness.
2. The first true thing that Corinna tells Lady Alicia is that she likes the rain.
3. Lady Rona is the deceased first wife of Lord Merton.
4. The only one to see Corinna slip off to the Cellar with hundreds of pins stuck in her clothes is the mournful old dog Taffy.
5. According to Corinna the Folk in the Northern Isles grow fierce during the Storms of the Equinox, which occur in the autumn and spring.
6. Corinna leaves her Folk bag in the Cellar because she doesn't want to accidentally lose the bag overboard while sailing with Finian.
7. Corinna shows Finian that she could coax the wind into the sails of the boat.
8. Corinna was given the name Stonewall by a matron at the foundling home because she was stubborn and wouldn't boil the soiled linens.
9. The Lady Rona's child is buried under the church eaves.
10. While in the Cellar Corinna realizes that she is not protected against Finian knowing she is responsible for the dogs destroying Edward's trophy skin.
11. Corinna should have known never to reveal any of her true convictions.
12. Old Francis disappears during the Storms of the Equinox.
13. The May Day garlands are scattered in a circle around the Manor to restrict the power of the Folk to the caverns.
14. Finian dresses up as a Cliffsend fisherman for the Masquerade Ball.""",
    3: """## Comprehension answer key — Section 3 (Chapters 9–11)
1. The Folk Keeper must always leap over the bonfire first.
2. Holding a brick of warm peat to your breast glows against the skin and gives a feeling of tranquility.
3. Corinna says that she will never marry.
4. When Corinna dives underwater to save Finian she is reborn; she no longer needs air, she can close her ears, and is weightless, which give her joy.
5. When another hand reaches for Corinna she sinks below the surface of the water because she was not ready to return to the world of laughter, tears and a past.
6. When Corinna finds her feet are sure and light up the cliff path it is as if she had memorized the cliff and knew all the crags.
7. Corinna believes Finian would laugh if he knew that the color of the hair inside her peat brick was red like his.
8. Corinna coaxes Finian to go sailing with her the next day.
9. After Corinna drips her blood into the ocean the sea's color turned dark, the waves arched with anger and a terrible storm began to brew.
10. After a wave smashes Corinna into the mast she realizes that the water around her ankles isn't coming from the rain and crashing waves, but from a crack in the boat's boards.
11. According to Corinna you cannot call the Sealfolk at low tide.
12. Everyone thinks breathing in is so important, but no one thinks about the importance of breathing out.
13. Corinna's mother goes mad and refuses to ever look at the sea when her husband Lord Merton burned her sealskin.
14. Sir Edward has hunted long enough to be able to tell when an animal is about to bolt.""",
    4: """## Comprehension answer key — Section 4 (Chapters 12–16)
1. The Folk did not frighten Corinna as much as she frightened herself.
2. When Corinna is alone she "can carve words from air and float them in a sea of rhyme." She has the last word.
3. Once Corinna emerges from the Cellar she realizes at once that the Manor is empty.
4. Corinna is transformed from savage to servant with a bar of soap and some servant's clothes borrowed from Mrs. Baines' storeroom.
5. While at the stonecutter's tray Corinna lingers over a tiny crafted quartz rooster that has a swagger and strut.
6. Finian pulls Corinna away from the crowd and down an alley at the Harvest Fair.
7. When Finian first met Corinna he knew by the way she carried herself that she was no boy.
8. Finian says that Corinna could come back from the sea for the Folk, for him, and to marry him.
9. The color of the strands of hair in Finian's peat brick on Midsummer's Eve was silver.
10. Finian and Lady Alicia have gone to Rhysbridge to testify before the courts that there is an heir with a greater claim than theirs to Marblehaugh Park.
11. Corinna could not confine herself to the land even for Finian whom she loved.
12. Taffy's grave is marked by dozens of amber beads glowing in the cool autumn sun.
13. The direction of the Seal Rock is built into Corinna's bones.
14. When Corinna's Sealskin is peeling away from her she is thankful she has her words because she could tell her story.""",
}


GLEAN_OPTIONS = """Choose ONE (or more!) of the guide's assignment options:

1. **Sealfolk research** — Research the mythical sealfolk and write a report on your findings. Include a sketch of what one might look like.
2. **A Celtic feast** — Choose a Celtic feast or celebration to research and write an essay on your findings. Research things like: What does it celebrate? What takes place? Why is it important? Is it still celebrated today?
3. **After the last page** — Imagine what Corinna's life is like after the finish of the novel. Write a few journal entries as if you were her, describing her new day-to-day activities.
4. **Corin vs. Corinna** — Create sketches or another type of visual representation of how you believe Corin and Corinna differed. Describe and label these differences, both in appearance and in action.
5. **A scene you can hold** — Create a diorama or draw a picture of a scene from the book.
6. **Three poems** — Corinna pens beautiful descriptions of her surroundings, especially the sea. Write three poems describing things you find beautiful. Be sure to use rich, specific adjectives and analogies. Practice reading your poetry aloud or even memorize some of your poems and present them to friends, family, or classmates."""



def _acquire_answer_key(section_number):
    words = next(s["vocab"] for s in SECTIONS if s["number"] == section_number)
    lines = [f"- **{w}** — {OFFICIAL_DEFINITIONS[w]}" for w in words]
    return (
        f"## Vocabulary key — Section {section_number}  ·  teacher reference only\n"
        + "\n".join(lines)
        + "\n\nThe publisher's definitions. Accept the child's own wording when it "
          "carries the same meaning."
    )


class Command(BaseCommand):
    help = "Seed the Blackbird 'The Folk Keeper' course + Socratic seminars (idempotent)."

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

        blueprint = get_blueprint("blackbird_the_folk_keeper")
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
                     "The Cellar, the cliffs, the sea, the Manor — and why each place matters to Corinna."),
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
            vocab_questions += [
                ("application",
                 SENTENCE_PROMPT.format(i=i, n=SENTENCE_COUNT),
                 SENTENCE_HINT)
                for i in range(1, SENTENCE_COUNT + 1)
            ]
            s, q = self._seed_set(
                acquire, family,
                title=f"Section {n} · Vocabulary",
                reading=chs,
                intro="Use a real dictionary — the paper kind! Define each word in your own "
                      "words. Then write five sentences — one per box, a different word in each.",
                rubric=ACQUIRE_RUBRIC,
                answer_key=_acquire_answer_key(n),
                questions=vocab_questions,
            )
            set_count += s; q_count += q

            # -- Recollect -------------------------------------------------
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

            # -- Explore: Writing ------------------------------------------
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
                     f"concluding sentence.\n\n\u201c{section['writing_prompt']}\u201d",
                     "Just get your thoughts on paper — the polish comes next."),
                    ("application",
                     "FINAL DRAFT — Thoroughly edit your rough draft, make any necessary "
                     "changes, then write your final version here using your best penmanship.",
                     "Check spelling, grammar, punctuation — and read it out loud to hear the flow."),
                ],
            )
            set_count += s; q_count += q

            # -- Explore: Discussion (the guide's own) — teacher-led --------
            s, q = self._seed_set(
                explore, family,
                title=f"Section {n} · Discussion",
                reading=chs,
                intro=DISCUSSION_INTRO,
                rubric=DISCUSSION_RUBRIC,
                questions=[(cat, prompt, "") for cat, prompt in section["discussion"]],
                mode=QuestionSet.MODE_DISCUSSION,
            )
            set_count += s; q_count += q

            # -- Explore: Socratic seminar (the app's standard) -------------
            s, q = self._seed_set(
                explore, family,
                title=f"Section {n} · Socratic Seminar",
                reading=chs,
                intro=SOCRATIC_INTRO,
                rubric=SOCRATIC_RUBRIC,
                questions=section["socratic"],
                mode=QuestionSet.MODE_DISCUSSION,
            )
            set_count += s; q_count += q

        # -- Glean ---------------------------------------------------------
        glean = self._lesson(curriculum, 5, 1)
        s, q = self._seed_set(
            glean, family,
            title="Section 5 · Glean: Final Project",
            reading="",
            intro=GLEAN_OPTIONS,
            rubric=GLEAN_RUBRIC,
            questions=[
                ("application",
                 "Which assignment option did you choose — and why does it fit you?",
                 "Pick the one you'd be most excited to make."),
                ("application",
                 "Make your plan: list your steps, what you need, and what 'finished' will look like.",
                 "A good plan has a few clear steps and a finish line."),
                ("application",
                 "When your project is done, reflect: what did it help you understand about "
                 "the story? What are you proudest of?",
                 "Tell the truth about what was fun and what was hard."),
            ],
        )
        set_count += s; q_count += q

        # ...and the hands-on option, ALONGSIDE the printed six rather than in
        # place of them. Four of the guide's own options end in writing; Kaylin
        # draws, and she read the book.
        from tutor import glean_handson

        book = glean_handson.BOOKS["folk_keeper"]
        hands_on = glean_handson.hands_on_title("folk_keeper")
        # Renaming a PROJECT must not leave the retired one beside its
        # replacement — the child would be offered both.
        glean_handson.retire_superseded(glean, hands_on)
        s, q = self._seed_set(
            glean, family,
            title=hands_on,
            reading="",
            intro=book["intro"],
            rubric=book["rubric"],
            questions=glean_handson.questions("folk_keeper"),
        )
        set_count += s; q_count += q

        CurriculumResource.objects.get_or_create(
            curriculum=curriculum,
            url="https://blackbirdandcompany.com/information-for-parents-and-teachers/answer-keys/the-folk-keeper/",
            defaults={
                "label": "Blackbird Answer Key — The Folk Keeper",
                "resource_type": CurriculumResource.ANSWER_KEY,
                "teacher_only": True,
                "order": 0,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {set_count} question sets, {q_count} questions. "
            f"{child.first_name} placed at "
            f"{'Section 1: Read' if placed else 'existing progress (kept)'}."
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
        # Drop stale questions beyond the current list — but never one a child
        # has already answered (that would orphan their saved response).
        stale = qset.questions.filter(order__gt=len(questions))
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {
                int(k) for k, v in (sheet.answers or {}).items()
                if str(v).strip() and str(k).isdecimal()
            }
        stale.exclude(pk__in=answered).delete()
        return 1, count
