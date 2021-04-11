from .shared import db, raise_if_invalid_data


class Event(db.Model):
    # pylint: disable=E1101
    name = db.Column(db.String(20), primary_key=True)
    event_start_time = db.Column(db.Integer)
    event_end_time = db.Column(db.Integer)
    # kill switch
    is_over = db.Column(db.Boolean)

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

    @property
    def as_json(self):
        return {
            "name": self.name,
            "event_start_time": self.event_start_time,
            "event_end_time": self.event_end_time,
            "is_over": self.is_over,
        }

    # pylint: enable=E1101
