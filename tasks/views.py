from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.serializers import ModelSerializer

from .models import Task, TaskDependency
from .services import detect_cycle, update_dependents, update_task_status


# ---------- SERIALIZER ----------
class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


# ---------- LIST & CREATE TASK ----------
class TaskListCreateView(ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


# ---------- UPDATE TASK STATUS ----------
class TaskUpdateView(APIView):
    def patch(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("status")
        if not new_status:
            return Response(
                {"error": "status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = new_status
        task.save()

        # 🔁 Auto-update dependents
        update_dependents(task.id)
        update_task_status(task.id)

        return Response(
            {
                "id": task.id,
                "status": task.status,
                "message": "Task status updated successfully"
            },
            status=status.HTTP_200_OK
        )


# ---------- ADD DEPENDENCY ----------
class AddDependencyView(APIView):
    def post(self, request, task_id):
        depends_on_id = request.data.get("depends_on_id")

        if not depends_on_id:
            return Response(
                {"error": "depends_on_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if int(task_id) == int(depends_on_id):
            return Response(
                {"error": "Task cannot depend on itself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cycle = detect_cycle(task_id, depends_on_id)
        if cycle:
            return Response(
                {
                    "error": "Circular dependency detected",
                    "cycle_path": cycle
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        TaskDependency.objects.create(
            task_id=task_id,
            depends_on_id=depends_on_id
        )

        return Response(
            {"message": "Dependency added successfully"},
            status=status.HTTP_201_CREATED
        )
