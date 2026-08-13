"""Seed the Spelling OS scope & sequence (idempotent).

Unit 1 (weeks 1-4) is deliberately remedial — short vowels, digraphs, the FLOSS
rule — because that is where Violet's phonics regression lives. If she flies
through it the auto-advance moves her on; if she doesn't, the app repeats the
week and tells the parent, which is itself the diagnosis.

Every dictation sentence uses only patterns taught at or before its own week, so
a week-2 sentence never asks her to spell a week-9 vowel team.

    python manage.py seed_spelling
    python manage.py seed_spelling --place Violet --for-user lopezjronald
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from spelling.models import SpellingPlacement, SpellingWeek, SpellingWord

# (word, sentence, sort_bucket)
UNIT_1 = [
    {
        "number": 1,
        "unit": "Foundation Repair",
        "pattern": "short a / short i",
        "rule": "One vowel between two consonants usually says its short sound: "
                "a as in cat, i as in pig.",
        "sort_buckets": ["short a", "short i"],
        "words": [
            ("cat", "The cat sat on my lap.", 0),
            ("map", "Dad has a big map.", 0),
            ("bag", "Put the ham in a bag.", 0),
            ("ham", "I had ham for lunch.", 0),
            ("tap", "Do not tap on the glass.", 0),
            ("sad", "The sad man lost his hat.", 0),
            ("hat", "My hat fell off.", 0),
            ("pig", "The pig is in the mud.", 1),
            ("bit", "I bit into the red apple.", 1),
            ("fix", "Dad can fix my bike.", 1),
            ("him", "I gave the map to him.", 1),
            ("dig", "We dig in the sand.", 1),
            ("rip", "Do not rip the bag.", 1),
            ("win", "I hope we win the game.", 1),
        ],
        "heart": [
            ("said", "She said hello to me.", "ai says short e"),
            ("was", "It was a hot day.", "a says short u, s says /z/"),
        ],
    },
    {
        "number": 2,
        "unit": "Foundation Repair",
        "pattern": "short o / short u / short e",
        "rule": "Short o as in dog, short u as in sun, short e as in bed. "
                "Blends put two consonants together and you hear both.",
        "sort_buckets": ["short o", "short u", "short e"],
        "words": [
            ("dog", "My dog ran to me.", 0),
            ("hop", "The frog can hop.", 0),
            ("rock", "I sat on a big rock.", 0),
            ("stop", "We stop at the red sign.", 0),
            ("crop", "The crop grew tall.", 0),
            ("sun", "The sun is hot.", 1),
            ("bug", "A bug is on my hand.", 1),
            ("must", "We must go to bed.", 1),
            ("drum", "He hit the drum.", 1),
            ("bed", "I made my bed.", 2),
            ("nest", "The bird has a nest.", 2),
            ("step", "Watch that big step.", 2),
            ("help", "Can you help me?", 2),
            ("desk", "My desk is a mess.", 2),
        ],
        "heart": [
            ("come", "Come with me to the shop.", "o says short u, silent e"),
            ("some", "I want some milk.", "o says short u, silent e"),
            ("what", "What is in the bag?", "a says short u"),
        ],
    },
    {
        "number": 3,
        "unit": "Foundation Repair",
        "pattern": "digraphs sh, ch, th, wh, ck",
        "rule": "Two letters, ONE sound. ck spells /k/ right after a short vowel "
                "at the end of a word.",
        "sort_buckets": ["sh / ch", "th / wh", "ck"],
        "words": [
            ("ship", "The ship is at sea.", 0),
            ("shop", "We shop for a hat.", 0),
            ("fish", "A fish swam past us.", 0),
            ("wish", "I wish for a dog.", 0),
            ("chin", "He hit his chin.", 0),
            ("chop", "Dad will chop the log.", 0),
            ("much", "That is too much.", 0),
            ("thin", "The stick is thin.", 1),
            ("bath", "I had a hot bath.", 1),
            ("with", "Come with us.", 1),
            ("when", "When can we go?", 1),
            ("whip", "The wind can whip the flag.", 1),
            ("duck", "A duck sat on the rock.", 2),
            ("sock", "I lost one sock.", 2),
            ("pack", "Pack your bag.", 2),
        ],
        "heart": [
            ("they", "They ran to the shop.", "ey says long a"),
            ("their", "That is their dog.", "eir says /air/"),
        ],
    },
    {
        "number": 4,
        "unit": "Foundation Repair",
        "pattern": "FLOSS rule + glued sounds",
        "rule": "FLOSS: at the end of a short word, double f, l, s and z. "
                "Glued sounds stick together: -ang, -ing, -onk, -unk.",
        "sort_buckets": ["FLOSS (ff/ll/ss/zz)", "-ang / -ing", "-onk / -unk"],
        "words": [
            ("off", "Take off your hat.", 0),
            ("cliff", "The cliff is steep.", 0),
            ("bell", "The bell will ring.", 0),
            ("hill", "We ran up the hill.", 0),
            ("tell", "Tell me what he said.", 0),
            ("miss", "I miss my dog.", 0),
            ("class", "My class is fun.", 0),
            ("dress", "She has a red dress.", 0),
            ("buzz", "The bugs buzz at us.", 0),
            ("bang", "The drum went bang.", 1),
            ("sang", "We sang with them.", 1),
            ("ring", "I lost my ring.", 1),
            ("king", "The king sat still.", 1),
            ("honk", "Cars honk on the hill.", 2),
            ("junk", "That box is full of junk.", 2),
        ],
        "heart": [
            ("who", "Who is at the door?", "wh says /h/, o says /oo/"),
            ("does", "Does he want help?", "oe says short u, s says /z/"),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the Spelling OS weeks and words. Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--place", help="Child first name to start at week 1.")
        parser.add_argument("--for-user", help="Parent username (with --place).")

    @transaction.atomic
    def handle(self, *args, **options):
        weeks = words = 0
        for spec in UNIT_1:
            week, created = SpellingWeek.objects.update_or_create(
                number=spec["number"],
                defaults={
                    "unit": spec["unit"],
                    "pattern": spec["pattern"],
                    "rule": spec["rule"],
                    "sort_buckets": spec["sort_buckets"],
                },
            )
            weeks += 1
            for order, (word, sentence, bucket) in enumerate(spec["words"]):
                SpellingWord.objects.update_or_create(
                    week=week, word=word,
                    defaults={"sentence": sentence, "sort_bucket": bucket,
                              "is_heart": False, "order": order},
                )
                words += 1
            for order, (word, sentence, tricky) in enumerate(spec["heart"]):
                SpellingWord.objects.update_or_create(
                    week=week, word=word,
                    defaults={"sentence": sentence, "is_heart": True,
                              "tricky_part": tricky, "order": order},
                )
                words += 1
            self.stdout.write(
                f"  Week {week.number}: {spec['pattern']} — "
                f"{len(spec['words'])} words + {len(spec['heart'])} heart"
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded {weeks} weeks, {words} words."))

        if options.get("place"):
            from django.contrib.auth import get_user_model
            from students.models import Student

            username = options.get("for_user")
            if not username:
                raise CommandError("--place needs --for-user.")
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f"No user '{username}'.")
            child = Student.objects.filter(
                parent=user, first_name__iexact=options["place"]).first()
            if child is None:
                raise CommandError(f"No child '{options['place']}' for {username}.")
            placement, made = SpellingPlacement.objects.get_or_create(
                child=child, defaults={"created_by": user})
            self.stdout.write(self.style.SUCCESS(
                f"{'Placed' if made else 'Already placed'} {child.first_name} "
                f"at week {placement.current_week}."
            ))
