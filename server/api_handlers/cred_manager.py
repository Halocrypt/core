class CredManager:
    user: str = None
    access_token: dict = None

    def __init__(self, access_token=None):
        self.access_token = access_token or {}
        self.user = self.access_token.get("user")
