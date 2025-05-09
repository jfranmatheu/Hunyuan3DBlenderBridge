import requests
from typing import List, Dict, Any

from ..session import get_session

def get_temp_messages() -> List[Dict[str, Any]] | None:
    """Fetches messages for the temporary mailbox associated with the provided session."""

    session = get_session()

    url = "https://web2.temp-mail.org/messages"
    headers = {
        # Mimic browser headers
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        # Cookies are handled by the session object
    }

    try:
        response = session.get(url, headers=headers, timeout=15) # Longer timeout for messages
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        if data and isinstance(data, dict) and "messages" in data and isinstance(data["messages"], list):
            # You could optionally add validation for the mailbox field against an expected value if needed
            # e.g., if expected_mailbox and data.get("mailbox") != expected_mailbox:
            #    print(f"❌ Error: Fetched messages for unexpected mailbox {data.get('mailbox')}")
            #    return None
            return data["messages"]
        else:
            # Handle cases like empty inbox (might return empty list or different structure)
            if isinstance(data, dict) and data.get("messages") == []:
                return [] # Return empty list if messages array is explicitly empty
            print(f"❌ Error: Unexpected response format from temp-mail messages endpoint: {data}")
            return None

    except requests.exceptions.Timeout:
        print(f"❌ Error: Request to {url} timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching temp messages: {e}")
        return None
    except Exception as e:
        # Catch potential JSON decoding errors or other unexpected issues
        print(f"❌ An unexpected error occurred while fetching messages: {e}")
        return None

# Example usage (assuming you have a session from get_temp_mailbox):
# if __name__ == "__main__":
#     # First, get a mailbox and establish a session
#     temp_session = requests.Session()
#     mailbox_info_resp = temp_session.get("https://web2.temp-mail.org/mailbox", headers=headers)
#     if mailbox_info_resp.ok:
#          mailbox_info = mailbox_info_resp.json()
#          print(f"Using mailbox: {mailbox_info.get('mailbox')}")
#          messages = get_temp_messages(temp_session)
#          if messages is not None:
#              print(f"📬 Found {len(messages)} messages:")
#              for msg in messages:
#                  print(f"  - From: {msg.get('from')}, Subject: {msg.get('subject')}")
#          else:
#              print("Failed to retrieve messages.")
#     else:
#         print("Failed to get initial mailbox.")
