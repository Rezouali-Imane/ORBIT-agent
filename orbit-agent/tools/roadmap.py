from pathlib import Path
import re

from langchain_core.tools import tool

from agent.schemas import Roadmap, roadmap_issues


ROADMAP_PATH = Path(__file__).resolve().parents[1] / "outputs" / "roadmap.md"


def _node_id(value: str, index: int) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_") or "task"
    return f"task_{index}_{slug[:30]}"


def render_mermaid(roadmap: Roadmap) -> str:
    lines = ["flowchart TD"]
    task_ids: dict[str, str] = {}
    task_index = 0

    for phase_index, phase in enumerate(roadmap.phases, start=1):
        phase_id = f"phase_{phase_index}"
        lines.append(f'    subgraph {phase_id}["{phase.name}"]')
        for task in phase.tasks:
            task_index += 1
            task_id = _node_id(task.name, task_index)
            task_ids[task.name] = task_id
            lines.append(f'        {task_id}["{task.name} ({task.duration_days}d)"]')
        lines.append("    end")

    for phase in roadmap.phases:
        for task in phase.tasks:
            for dependency in task.depends_on:
                if dependency in task_ids:
                    lines.append(f"    {task_ids[dependency]} --> {task_ids[task.name]}")

    return "\n".join(lines)


@tool("create_roadmap")
def create_roadmap(roadmap: Roadmap) -> str:
    """Validate, render, and save a structured project roadmap as Mermaid."""
    issues = roadmap_issues(roadmap)
    if issues:
        return "Roadmap was not created:\n- " + "\n- ".join(issues)

    mermaid = render_mermaid(roadmap)
    output = f"# {roadmap.title}\n\n```mermaid\n{mermaid}\n```\n"
    ROADMAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    ROADMAP_PATH.write_text(output, encoding="utf-8")
    return output