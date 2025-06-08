import hashlib
import json
import os
import time
import urllib.parse

from dotenv import load_dotenv


def generate_sso_url(username: str) -> str:
    """
    Generates a valid SSO URL for testing by reading configuration
    from the .env.local file.
    """
    # Load environment variables from .env.local
    load_dotenv(dotenv_path=".env.local")

    # --- Read Configuration from Environment ---
    listen_port = os.getenv("LISTEN_PORT", "8080")
    listen_prefix = os.getenv("LISTEN_PREFIX", "").strip()

    # Clean up the prefix to ensure it's a valid URL path component
    if listen_prefix.endswith("/"):
        listen_prefix = listen_prefix[:-1]
    if listen_prefix and not listen_prefix.startswith("/"):
        listen_prefix = "/" + listen_prefix

    base_url = f"http://localhost:{listen_port}{listen_prefix}"

    sso_secrets_str = os.getenv("SSO_APP_SECRETS")
    if not sso_secrets_str:
        raise ValueError("SSO_APP_SECRETS not found in .env.local file.")

    try:
        # The value from .env file is a string, so we need to parse it as JSON
        sso_secrets = json.loads(sso_secrets_str)
        app_id = next(iter(sso_secrets))
        app_secret = sso_secrets[app_id]
    except (json.JSONDecodeError, StopIteration) as e:
        raise ValueError(f"Could not parse SSO_APP_SECRETS from .env.local. Error: {e}")

    current_time = str(int(time.time()))

    # 1. Construct the string for signing
    string_to_sign = f"appId={app_id}&appSecret={app_secret}&username={username}&time={current_time}"

    # 2. Calculate the MD5 hash
    sign = hashlib.md5(string_to_sign.encode()).hexdigest()

    # 3. Assemble the URL parameters
    params = {"appId": app_id, "username": username, "time": current_time, "sign": sign}

    # 4. Build the final URL
    query_string = urllib.parse.urlencode(params)
    full_url = f"{base_url}/ssologin?{query_string}"

    return full_url


if __name__ == "__main__":
    import sys

    # Check for username argument, otherwise default to 'testuser'
    if len(sys.argv) > 1:
        test_username = sys.argv[1]
    else:
        test_username = "testuser"

    try:
        url = generate_sso_url(test_username)
        print("Generated SSO URL:")
        print(url)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        print("Please ensure the .env.local file exists in the same directory and is correctly formatted.")
