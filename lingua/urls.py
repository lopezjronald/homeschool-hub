from django.urls import path

app_name = "lingua"

# Views arrive with the reading UI (LGA-47+). Namespace reserved now so links
# resolve as `lingua:<name>` from day one.
urlpatterns = [
    # path("", views.home, name="home"),
]
