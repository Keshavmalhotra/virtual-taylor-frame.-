from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class NamedRegion:
    name: str
    start_row: int
    start_col: int
    end_row: int
    end_col: int

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "start_row": self.start_row + 1, "start_col": self.start_col + 1,
                "end_row": self.end_row + 1, "end_col": self.end_col + 1}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NamedRegion":
        return cls(str(data["name"]), int(data["start_row"]) - 1, int(data["start_col"]) - 1,
                   int(data["end_row"]) - 1, int(data["end_col"]) - 1)
