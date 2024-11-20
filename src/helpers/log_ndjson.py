"""Log function to log to NDJSON file."""

import json
import time
import random


def log_ndjson(file_path, retry: int = 10, **data) -> None:
    """
    Log data to NDJSON file.

    Append all provided data as a single line to the file.

    Parameters
    ----------
    file_path : str
        File path to log to.
    data : dict
        Data to log.
    retry : int, optional
        Number of retries if the logging operation fails (default is 10).

    Raises
    ------
    IOError
        If the data could not be logged to the file after the number of retries due to file-related issues.
    """
    attempt = 0
    while attempt < retry:
        try:
            with open(file_path, "a") as file:
                file.write(json.dumps(data) + "\n")
            break

        except (OSError, IOError) as e:
            attempt += 1

            if attempt >= retry:
                raise IOError(f"Failed to log data after {retry} attempts due to: {str(e)}") from e

            time.sleep(random.uniform(0, 1))  # nosec
