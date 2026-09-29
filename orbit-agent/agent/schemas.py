from pydantic import BaseModel, Field


class RoadmapTask(BaseModel):
    name: str = Field(min_length=1)
    duration_days: int = Field(gt=0)
    depends_on: list[str] = Field(default_factory=list)


class RoadmapPhase(BaseModel):
    name: str = Field(min_length=1)
    tasks: list[RoadmapTask] = Field(min_length=1)


class Roadmap(BaseModel):
    title: str = Field(min_length=1)
    phases: list[RoadmapPhase] = Field(min_length=1)


def roadmap_issues(roadmap: Roadmap) -> list[str]:
    tasks = [task for phase in roadmap.phases for task in phase.tasks]
    names = [task.name for task in tasks]
    issues: list[str] = []

    if len(names) != len(set(names)):
        issues.append("task names must be unique")

    known_names = set(names)
    for task in tasks:
        unknown = sorted(set(task.depends_on) - known_names)
        if unknown:
            issues.append(f"{task.name} depends on unknown task(s): {', '.join(unknown)}")
        if task.name in task.depends_on:
            issues.append(f"{task.name} cannot depend on itself")

    graph = {
        task.name: set(task.depends_on).intersection(known_names)
        for task in tasks
    }
    while graph:
        ready = {name for name, dependencies in graph.items() if not dependencies}
        if not ready:
            issues.append("dependencies contain a cycle")
            break
        for name in ready:
            graph.pop(name)
        for dependencies in graph.values():
            dependencies.difference_update(ready)

    return issues