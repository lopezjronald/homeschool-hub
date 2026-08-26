from tutor.models import QuestionSet
rows = list(QuestionSet.objects.filter(title__icontains="Glean").values_list("id", "title", "status"))
print("GLEAN SETS IN PROD:", len(rows))
for r in rows:
    print("  ", r)
