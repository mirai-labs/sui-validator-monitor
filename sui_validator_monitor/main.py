import os
import re
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

METRICS_URL = os.environ["METRICS_URL"]
PUSHOVER_APP_TOKEN = os.environ["PUSHOVER_APP_TOKEN"]
PUSHOVER_USER_KEY = os.environ["PUSHOVER_USER_KEY"]

client = httpx.Client()


def send_notification(
    message: str,
):
    data = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    client.post(
        "https://api.pushover.net/1/messages.json",
        headers=headers,
        data=data,
    )
    return


def get_last_executed_checkpoint() -> int:
    r = client.get(METRICS_URL)
    for line in r.text.split("\n"):
        if line.startswith("last_executed_checkpoint"):
            matches = re.findall(r"last_executed_checkpoint\s+(\d+)", line)
            if len(matches) > 0:
                checkpoint = int(matches[0])
                return checkpoint


def main():
    previous_checkpoint = None
    rounds = 3
    interval = 5

    for round in range(1, rounds + 1):
        try:
            current_checkpoint = get_last_executed_checkpoint()
            print(f"Round {round}: Checkpoint = {current_checkpoint}")

            if previous_checkpoint is not None:
                if not current_checkpoint > previous_checkpoint:
                    print("Sending alert!")
                    send_notification(f"Validator is down: {METRICS_URL}")

            previous_checkpoint = current_checkpoint

            if round < rounds:
                print(f"Waiting {interval} seconds before next check...")
                time.sleep(interval)

        except Exception as e:
            print(f"Error in round {round}: {str(e)}")
            send_notification(f"Validator is down: {METRICS_URL}")
            break


if __name__ == "__main__":
    main()
