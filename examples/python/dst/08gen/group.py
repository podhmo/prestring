import typing as t
import dataclasses
from .user import User
@dataclasses.dataclass
class Group:
    name: str
    members: t.List[User] = dataclasses.field(default_factory=list)