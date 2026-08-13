from django.contrib import admin

from .models import SpellingCard, SpellingPlacement, SpellingSession, SpellingWeek, SpellingWord


class WordInline(admin.TabularInline):
    model = SpellingWord
    extra = 0


@admin.register(SpellingWeek)
class SpellingWeekAdmin(admin.ModelAdmin):
    list_display = ("number", "unit", "pattern")
    inlines = [WordInline]


admin.site.register([SpellingCard, SpellingPlacement, SpellingSession])
