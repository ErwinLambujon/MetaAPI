import requests
from datetime import datetime, timedelta

class FacebookAPI:
    def __init__(self, app_id, app_secret, user_access_token, page_id):
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_access_token = user_access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.page_access_token = None

    def get_long_lived_token(self):
        endpoint = f"{self.base_url}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": self.user_access_token
        }
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                return None
        except Exception:
            return None

    def get_page_access_token(self, long_lived_token):
        endpoint = f"{self.base_url}/{self.page_id}"
        params = {
            "access_token": long_lived_token,
            "fields": "access_token"
        }
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                return None
        except Exception:
            return None

    def setup_tokens(self):
        long_lived_token = self.get_long_lived_token()
        if not long_lived_token:
            return False
        self.page_access_token = self.get_page_access_token(long_lived_token)
        return self.page_access_token is not None

    def get_conversation_threads(self, limit=25):
        endpoint = f"{self.base_url}/{self.page_id}/conversations"
        params = {
            "access_token": self.page_access_token,
            "limit": limit,
            "fields": "participants,updated_time,message_count,unread_count"
        }
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception:
            return None

    def get_conversation_messages(self, conversation_id, limit=100):
        endpoint = f"{self.base_url}/{conversation_id}/messages"
        params = {
            "access_token": self.page_access_token,
            "limit": limit,
            "fields": "message,created_time,from"
        }
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception:
            return None

    def get_all_recent_messages(self, days_ago=30):
        if not self.page_access_token:
            return []

        all_messages = []
        threads = self.get_conversation_threads()

        if not threads or 'data' not in threads:
            return []

        cutoff_date = datetime.now() - timedelta(days=days_ago)

        for thread in threads['data']:
            updated_time = datetime.strptime(thread['updated_time'], '%Y-%m-%dT%H:%M:%S%z')

            if updated_time.replace(tzinfo=None) < cutoff_date:
                continue

            messages = self.get_conversation_messages(thread['id'])
            if messages and 'data' in messages:
                all_messages.extend(messages['data'])

        return all_messages


def main():
    APP_ID = "1213457369979485"
    APP_SECRET = "00c0a366fe8cbcba8195f16febaad5d9"
    USER_ACCESS_TOKEN = ("EAARPog982l0BO8RMFZCyeLEdZBLgLF9YwFwVdPyh4klDXgr5"
                         "LaqP0YTSoLiZA0ZAi9MvJIgHR7F9ow8u0ZBgcV4YO4ZC0QKdSG"
                         "CSPjioCaAQwttmcZCZAV4jhTThETc1cot9Ej8BCZC42ZCbd2bZA"
                         "JIRndQU5wzCKMEpuAzKIU9GgfwPPFv2SBLgkDh0AhzRljvpiKoiD"
                         "lLegFmRJrXD24L9W1znQbURyMZD")  # This is your current ACCESS_TOKEN

    PAGE_ID = "105152451415006"

    fb_api = FacebookAPI(APP_ID, APP_SECRET, USER_ACCESS_TOKEN, PAGE_ID)

    if not fb_api.setup_tokens():
        return

    messages = fb_api.get_all_recent_messages(days_ago=30)

    if messages:
           print(f"\nFound {len(messages)} messages:")
           for msg in messages:
                  print(f"""
    Message ID: {msg.get('id')}
    From: {msg.get('from', {}).get('name')}
    Time: {msg.get('created_time')}
    Message: {msg.get('message')}
    {'=' * 50}
    """)
    else:
           print("No messages found or error occurred")


if __name__ == "__main__":
    main()
