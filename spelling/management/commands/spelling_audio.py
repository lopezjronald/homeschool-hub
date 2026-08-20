"""Bake the spelling words and their sentences to real speech (idempotent).

Runs where AWS credentials and the public asset bucket live — locally if you
have both, otherwise ``heroku run`` on the dyno, same as lingua's image bake.

    python manage.py spelling_audio                    # every unbaked word
    python manage.py spelling_audio --week 1 --force   # re-bake week 1
    python manage.py spelling_audio --voice Danielle   # try another voice

Voices worth trying (US English): Joanna (default, clear and warm), Danielle,
Ruth, Kendra, Salli, Ivy (child), Matthew, Stephen. Changing the voice changes
the content hash, so a re-bake writes new objects rather than overwriting.
"""

from django.core.management.base import BaseCommand, CommandError

from spelling import audio as spelling_audio
from spelling.models import SpellingWord


class Command(BaseCommand):
    help = "Synthesize word + sentence audio for spelling words. Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--week", type=int, help="Only this week number.")
        parser.add_argument("--voice", default=spelling_audio.DEFAULT_VOICE)
        parser.add_argument("--engine", default=spelling_audio.DEFAULT_ENGINE)
        parser.add_argument(
            "--force", action="store_true",
            help="Re-bake words that already have audio (use after a voice change).")
        parser.add_argument(
            "--limit", type=int, help="Stop after this many words (a cheap trial).")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Say what would be baked without calling Polly.")

    def handle(self, *args, **options):
        from lingua import storage as lingua_storage

        words = SpellingWord.objects.select_related("week").order_by(
            "week__number", "is_heart", "order")
        if options.get("week"):
            words = words.filter(week__number=options["week"])
        if not options["force"]:
            words = words.filter(audio_url="")
        words = list(words)
        if options.get("limit"):
            words = words[: options["limit"]]

        if not words:
            self.stdout.write("Nothing to bake — every word already has audio.")
            return

        voice, engine = options["voice"], options["engine"]
        self.stdout.write(
            f"Baking {len(words)} word(s) with {voice} / {engine}"
            + (" [dry run]" if options["dry_run"] else "")
        )
        if options["dry_run"]:
            for w in words:
                self.stdout.write(f"  would bake: {w.word} — {w.sentence}")
            return

        done = failed = 0
        for word in words:
            try:
                # Two clips: the word on its own, said slowly, and the sentence
                # it lives in. A child dictating needs both — the word to spell,
                # and the sentence so she knows WHICH word ("their" vs "there").
                word_audio, word_key = spelling_audio.synthesize(
                    word.word, kind="word", voice=voice, engine=engine)
                sent_audio, sent_key = spelling_audio.synthesize(
                    word.sentence, kind="sentence", voice=voice, engine=engine)
                word.audio_url = lingua_storage.save_bytes(word_key, word_audio)
                word.sentence_audio_url = lingua_storage.save_bytes(sent_key, sent_audio)
                word.audio_voice = voice
                word.save(update_fields=["audio_url", "sentence_audio_url", "audio_voice"])
                done += 1
                self.stdout.write(f"  {word.week.number:>2} {word.word}")
            except spelling_audio.SpellingTTSError as exc:
                # Batch-resilient, like the other bakes: one bad word must not
                # cost the whole run.
                failed += 1
                self.stderr.write(self.style.WARNING(f"  {word.word}: {exc}"))

        self.stdout.write(self.style.SUCCESS(f"Baked {done} word(s)."))
        if failed:
            raise CommandError(f"{failed} word(s) failed — re-run to retry just those.")
