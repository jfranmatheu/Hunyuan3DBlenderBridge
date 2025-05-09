import requests

from ..session import get_session


def get_temp_mailbox() -> str | None:
    """Fetches a new temporary mailbox address from temp-mail.org using the provided session."""

    session = get_session()
    url = "https://web2.temp-mail.org/mailbox"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Origin": "https://temp-mail.org",
        "Referer": "https://temp-mail.org/",
        "Sec-Ch-Ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Sec-Gpc": "1",
    }

    try:
        response = session.get(url, headers=headers, timeout=10) # Add a timeout
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        if data and isinstance(data, dict) and "mailbox" in data:
            return data["mailbox"]
        else:
            print(f"❌ Error: Unexpected response format from temp-mail: {data}")
            return None

    except requests.exceptions.Timeout:
        print(f"❌ Error: Request to {url} timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching temp mailbox: {e}")
        return None
    except Exception as e:
        # Catch potential JSON decoding errors or other unexpected issues
        print(f"❌ An unexpected error occurred: {e}")
        return None

# Example usage (optional):
# if __name__ == "__main__":
#     mailbox = get_temp_mailbox()
#     if mailbox:
#         print(f"📬 Got temporary mailbox: {mailbox}")
#     else:
#         print("Failed to get temporary mailbox.")

