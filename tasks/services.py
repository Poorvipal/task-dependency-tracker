from .models import Task, TaskDependency


def detect_cycle(task_id, depends_on_id):
    """
    Detect circular dependency using DFS
    """
    graph = {}
    for dep in TaskDependency.objects.all():
        graph.setdefault(dep.task_id, []).append(dep.depends_on_id)

    graph.setdefault(task_id, []).append(depends_on_id)

    visited = set()
    stack = []

    def dfs(node):
        if node in stack:
            return stack[stack.index(node):] + [node]

        if node in visited:
            return None

        visited.add(node)
        stack.append(node)

        for neighbor in graph.get(node, []):
            cycle = dfs(neighbor)
            if cycle:
                return cycle

        stack.pop()
        return None

    return dfs(task_id)


def update_task_status(task_id):
    """
    Automatically update task status based on dependencies
    """
    task = Task.objects.get(id=task_id)
    dependencies = task.dependencies.all()

    if not dependencies.exists():
        return

    dependency_statuses = [dep.depends_on.status for dep in dependencies]

    if 'blocked' in dependency_statuses:
        task.status = 'blocked'
    elif all(status == 'completed' for status in dependency_statuses):
        task.status = 'in_progress'
    else:
        task.status = 'pending'

    task.save()


def update_dependents(task_id):
    """
    Update all tasks that depend on the given task
    """
    dependents = TaskDependency.objects.filter(depends_on_id=task_id)

    for dep in dependents:
        update_task_status(dep.task_id)
