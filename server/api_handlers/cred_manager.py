from sqlalchemy.sql.expression import false


class CredManager:
    user: str = None
    access_token: dict = None
    is_admin: bool = False

    def __init__(self, access_token=None):
        self.access_token = access_token or {}
        self.user = self.access_token.get("user")
        self.is_admin = self.access_token.get("is_admin", False)
