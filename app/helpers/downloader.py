import logging
import os
import time
from pathlib import Path

import requests
from tqdm import tqdm

from app.helpers.integrity_checker import check_file_integrity

logger = logging.getLogger(__name__)

_MAX_ATTEMPTS = 5
_CONNECT_TIMEOUT = 15
_READ_TIMEOUT = 60
_CHUNK_SIZE = 1024 * 1024


def _content_length(response) -> int:
    try:
        return int(response.headers.get("content-length", 0))
    except (TypeError, ValueError):
        return 0


def download_file(model_name: str, file_path: str, correct_hash: str, url: str, max_attempts: int = _MAX_ATTEMPTS) -> bool:
    """Download ``url`` to ``file_path`` with retries, resume and hash verification.

    Partially downloaded data is kept in ``<file_path>.part`` so an interrupted
    download can resume from where it stopped (via HTTP Range).
    """
    path = Path(file_path)
    if path.is_file() and check_file_integrity(str(path), correct_hash):
        print(f"\nSkipping {model_name} as it is already downloaded!")
        return True

    path.parent.mkdir(parents=True, exist_ok=True)
    part_path = Path(str(path) + ".part")

    for attempt in range(1, max_attempts + 1):
        existing = part_path.stat().st_size if part_path.is_file() else 0
        # 'identity' keeps byte ranges valid (gzip content-encoding breaks resume).
        headers = {"Accept-Encoding": "identity"}
        if existing:
            headers["Range"] = f"bytes={existing}-"
        try:
            print(f"\nDownloading {model_name} from {url}" + (f" (resuming at {existing} bytes)" if existing else ""))
            with requests.get(url, stream=True, headers=headers, timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT)) as response:
                if existing and response.status_code == 200:
                    # Server ignored the Range request -> start over.
                    existing = 0
                    part_path.unlink(missing_ok=True)
                response.raise_for_status()

                remaining = _content_length(response)
                total = existing + remaining if remaining else None
                mode = "ab" if existing else "wb"
                with tqdm(total=total, initial=existing, unit="B", unit_scale=True, desc=model_name) as bar:
                    with open(part_path, mode) as file:
                        for chunk in response.iter_content(_CHUNK_SIZE):
                            if chunk:
                                file.write(chunk)
                                bar.update(len(chunk))

            if check_file_integrity(str(part_path), correct_hash):
                os.replace(part_path, path)
                print(f"File integrity verified successfully: {file_path}")
                return True

            print(f"Integrity check failed for {file_path} (attempt {attempt}/{max_attempts}).")
            logger.warning("Integrity check failed for %s (attempt %d/%d)", model_name, attempt, max_attempts)
            part_path.unlink(missing_ok=True)
        except requests.exceptions.RequestException as exc:
            logger.warning("Download error for %s (attempt %d/%d): %s", model_name, attempt, max_attempts, exc)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Unexpected error downloading %s", model_name)

        if attempt < max_attempts:
            time.sleep(2 * attempt)

    print(f"Failed to download {model_name} after {max_attempts} attempts.")
    return False
