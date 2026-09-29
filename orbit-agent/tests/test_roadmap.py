from agent.schemas import Roadmap, RoadmapPhase, RoadmapTask, roadmap_issues
from tools import roadmap as roadmap_tool


def test_create_roadmap_renders_and_saves_mermaid(tmp_path, monkeypatch):
    output_path = tmp_path / "roadmap.md"
    monkeypatch.setattr(roadmap_tool, "ROADMAP_PATH", output_path)
    roadmap = Roadmap(
        title="Launch",
        phases=[
            RoadmapPhase(
                name="Build",
                tasks=[RoadmapTask(name="API", duration_days=2)],
            ),
            RoadmapPhase(
                name="Release",
                tasks=[
                    RoadmapTask(
                        name="Deploy",
                        duration_days=1,
                        depends_on=["API"],
                    )
                ],
            ),
        ],
    )

    result = roadmap_tool.create_roadmap.invoke(
        {"roadmap": roadmap.model_dump()}
    )

    assert "```mermaid" in result
    assert "API (2d)" in result
    assert "Deploy (1d)" in result
    assert "-->" in result
    assert output_path.read_text(encoding="utf-8") == result


def test_roadmap_rejects_impossible_dependency():
    roadmap = Roadmap(
        title="Broken",
        phases=[
            RoadmapPhase(
                name="Build",
                tasks=[
                    RoadmapTask(name="API", duration_days=2, depends_on=["Missing"])
                ],
            )
        ],
    )

    assert roadmap_issues(roadmap) == [
        "API depends on unknown task(s): Missing"
    ]