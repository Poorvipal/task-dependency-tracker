from django.contrib import admin
from .models import Task, TaskDependency

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("title",)

@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "depends_on")
