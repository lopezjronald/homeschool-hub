"""Bake single-utterance AudioClips for phonics / alphabet / phrases (LGA-84/86).

Run LOCALLY for Polly synthesis. On prod use ``--link-only`` after R2 upload
(same pattern as ``tts_build``). Never called from a request path.

    python manage.py clips_build --phonics --alphabet --phrases
    python manage.py clips_build --all --link-only
    python manage.py clips_build --phonics --force
"""
from django.core.management.base import BaseCommand, CommandError

from lingua import services


class Command(BaseCommand):
    help = "Bake (or --link-only) AudioClips for phonics, alphabet, and tutor phrases."

    def add_arguments(self, parser):
        parser.add_argument("--phonics", action="store_true",
                            help="Bake PhonicsRule practice words (LGA-84).")
        parser.add_argument("--alphabet", action="store_true",
                            help="Bake AlphabetTile spoken names + examples (LGA-86).")
        parser.add_argument("--phrases", action="store_true",
                            help="Bake TutorPacket practice lines (LGA-86).")
        parser.add_argument("--classroom", action="store_true",
                            help="Bake the parent's ClassroomPhrase session lines (LGA-94).")
        parser.add_argument("--travel", action="store_true",
                            help="Bake the adult TravelPhrase phrasebook (LGA-103).")
        parser.add_argument("--all", action="store_true",
                            help="Shorthand for every category above.")
        parser.add_argument("--voice", default=None, help="Polly voice (default: settings).")
        parser.add_argument("--engine", default=None, help="Polly engine (default: settings).")
        parser.add_argument("--link-only", action="store_true",
                            help="Prod: link rows from already-uploaded R2 assets, no Polly.")
        parser.add_argument("--force", action="store_true",
                            help="Re-bake even if a current clip already exists.")

    def handle(self, *args, **options):
        phonics = options["phonics"] or options["all"]
        alphabet = options["alphabet"] or options["all"]
        phrases = options["phrases"] or options["all"]
        classroom = options["classroom"] or options["all"]
        travel = options["travel"] or options["all"]
        if not (phonics or alphabet or phrases or classroom or travel):
            raise CommandError(
                "Pass --phonics, --alphabet, --phrases, --classroom, --travel, "
                "and/or --all."
            )

        texts = services.clip_texts_to_bake(
            phonics=phonics, alphabet=alphabet, phrases=phrases, classroom=classroom,
            travel=travel,
        )
        if not texts:
            self.stdout.write("No matching texts to bake (seed phonics/alphabet/packets first).")
            return

        baked = linked = skipped = failed = 0
        for text in texts:
            try:
                obj, action = services.bake_audio_clip(
                    text, voice=options["voice"], engine=options["engine"],
                    link_only=options["link_only"], force=options["force"],
                )
            except Exception as exc:  # noqa: BLE001 — one failure must not abort the batch
                failed += 1
                self.stderr.write(f"  {text!r} failed: {type(exc).__name__}: {exc}")
                continue
            if action == "baked":
                baked += 1
            elif action == "linked":
                linked += 1
            else:
                skipped += 1
            self.stdout.write(f"[{action}] {text!r} -> {obj.audio_key}")
        self.stdout.write(self.style.SUCCESS(
            f"Done: {baked} baked, {linked} linked, {skipped} skipped, {failed} failed "
            f"({len(texts)} texts)."
        ))
        # Exit non-zero when EVERYTHING failed — otherwise a deploy step goes green on
        # a total outage and the pages silently render without audio.
        if failed and not (baked or linked):
            raise CommandError(f"All {failed} clip(s) failed — nothing was baked or linked.")
