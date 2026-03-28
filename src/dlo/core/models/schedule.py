import json

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional

from dlo.common.schema import SchemaMixin
from dlo.core.config import Project


@dataclass
class ScheduleNode(SchemaMixin):
    cron: str
    nodes: list[str] = field(default_factory=list)
    job_info: Optional[dict] = field(default=None)


@dataclass
class Schedule(SchemaMixin):
    schedule_path: Path
    schedules: Mapping[str, ScheduleNode] = field(default_factory=dict)

    @classmethod
    def __from_project__(cls, project: Project):
        schedule_path = project.project_root_path / "schedule.json"

        if schedule_path.exists():
            data = json.loads(schedule_path.read_text())
        else:
            data = {}

        data["schedule_path"] = schedule_path

        return cls.from_dict(data)

    def save(self):
        schedules = self.to_dict()
        schedules.pop("schedule_path")

        self.schedule_path.write_text(json.dumps(schedules))
