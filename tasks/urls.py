from django.urls import path
from .views import (
    TaskListCreateView,
    AddDependencyView,
    TaskUpdateView,
)

urlpatterns = [
    path("tasks/", TaskListCreateView.as_view()),
    path("tasks/<int:task_id>/", TaskUpdateView.as_view()),
    path("tasks/<int:task_id>/dependencies/", AddDependencyView.as_view()),
]
