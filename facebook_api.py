import requests
from datetime import datetime, timedelta
import json

class FacebookAPI:
    def __init__(self, app_id, app_secret, user_access_token, page_id):
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_access_token = user_access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.page_access_token = None

    def verify_token(self, token):
        """Verify token permissions and expiration"""
        print("\nVerifying token...")
        endpoint = f"{self.base_url}/debug_token"
        params = {
            "input_token": token,
            "access_token": token
        }

        try:
            response = requests.get(endpoint, params=params)
            return response.status_code == 200
        except Exception as e:
            print(f"Error verifying token: {e}")
            return False

    def get_long_lived_token(self):
        """Convert short-lived token to long-lived token"""
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
                print(f"Error getting long-lived token: {response.text}")
                return None
        except Exception as e:
            print(f"Exception getting long-lived token: {e}")
            return None

    def get_page_access_token(self, long_lived_token):
        """Get page access token using long-lived user token"""
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
                print(f"Error getting page access token: {response.text}")
                return None
        except Exception as e:
            print(f"Exception getting page access token: {e}")
            return None

    def setup_tokens(self):
        """Complete token setup process"""
        if not self.verify_token(self.user_access_token):
            print("Initial token verification failed!")
            return False

        long_lived_token = self.get_long_lived_token()
        if not long_lived_token:
            print("Failed to get long-lived token!")
            return False

        self.page_access_token = self.get_page_access_token(long_lived_token)
        if not self.page_access_token:
            print("Failed to get page access token!")
            return False

        print("Token setup completed successfully!")
        return True

    def get_conversation_threads(self, limit=25):
        """Retrieve conversation threads for the page"""
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
                print(f"Error retrieving threads: {response.text}")
                return None
        except Exception as e:
            print(f"Exception retrieving threads: {e}")
            return None

    def get_conversation_messages(self, conversation_id, limit=100):
        """Retrieve messages from a specific conversation"""
        endpoint = f"{self.base_url}/{conversation_id}/messages"
        params = {
            "access_token": self.page_access_token,
            "limit": limit,
            "fields": "message,created_time,from,to"
        }

        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error retrieving messages: {response.text}")
                return None
        except Exception as e:
            print(f"Exception retrieving messages: {e}")
            return None

    def get_all_recent_messages(self, days_ago=30):
        """Retrieve all messages from recent conversations"""
        if not self.page_access_token:
            print("No page access token available. Run setup_tokens() first.")
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
