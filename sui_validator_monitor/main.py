import os
import re
import time

import httpx

METRICS_URL = os.environ["METRICS_URL"]

client = httpx.Client()


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
    interval = 1

    for round in range(1, rounds + 1):
        try:
            current_checkpoint = get_last_executed_checkpoint()
            print(f"Round {round}: Checkpoint = {current_checkpoint}")

            if previous_checkpoint is not None:
                assert (
                    current_checkpoint > previous_checkpoint
                ), f"Round {round}: Current checkpoint ({current_checkpoint}) is not higher than previous checkpoint ({previous_checkpoint})"
                print(f"Assertion passed: {current_checkpoint} > {previous_checkpoint}")

            previous_checkpoint = current_checkpoint

            if round < rounds:
                print(f"Waiting {interval} seconds before next check...")
                time.sleep(interval)

        except Exception as e:
            print(f"Error in round {round}: {str(e)}")
            break


if __name__ == "__main__":
    main()
