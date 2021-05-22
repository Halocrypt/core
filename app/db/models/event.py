from .base import Base
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from ..shared import raise_if_invalid_data


class Event(Base):
    __tablename__ = "event"
    __mapper_args__ = {"eager_defaults": True}
    # pylint: disable=E1101
    name = Column(String(20), primary_key=True)
    event_start_time = Column(Integer)
    event_end_time = Column(Integer)
    notifications = Column(ARRAY(JSONB))
    # kill switch
    is_over = Column(Boolean)

    def __init__(
        self,
        name: str,
        event_start_time: int = None,
        event_end_time: int = None,
        is_over: bool = False,
    ) -> None:
        raise_if_invalid_data(name, event_start_time, event_end_time)
        self.name = name
        self.event_start_time = event_start_time
        self.event_end_time = event_end_time
        self.is_over = is_over
        self.notifications = []

    @property
    def as_json(self):
        return {
            "name": self.name,
            "event_start_time": self.event_start_time,
            "event_end_time": self.event_end_time,
            "is_over": self.is_over,
        }

    # pylint: enable=E1101
