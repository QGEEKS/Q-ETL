import requests

class PushoverClient:
    API_URL = "https://api.pushover.net/1/messages.json"

    def __init__(self, app_token: str, user_key: str):
        """
        :param app_token: Pushover application token
        :param user_key: Pushover user/group key
        """
        self.app_token = app_token
        self.user_key = user_key

    def send(
        self,
        message: str,
        title: str | None = None,
        priority: int = 0,
        sound: str | None = None,
        url: str | None = None,
        url_title: str | None = None,
    ) -> dict:
        payload = {
            "token": self.app_token,
            "user": self.user_key,
            "message": message,
            "priority": priority,
        }

        if title:
            payload["title"] = title
        if sound:
            payload["sound"] = sound
        if url:
            payload["url"] = url
        if url_title:
            payload["url_title"] = url_title

        response = requests.post(self.API_URL, data=payload, timeout=10)
        response.raise_for_status()

        return response.json()
    
    """
    pushover = PushoverClient(
    app_token="APP_TOKEN_HER",
    user_key="USER_KEY_HER"
    )

    pushover.send(
        message="ETL-jobbet er færdigt ✅",
        title="Status",
        priority=0,
        sound="magic"
    )
    """