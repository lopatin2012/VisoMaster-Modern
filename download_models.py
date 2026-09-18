import sys

from app.helpers.downloader import download_file
from app.processors.models_data import models_list

failed = []
for model_data in models_list:
    ok = download_file(
        model_data['model_name'],
        model_data['local_path'],
        model_data['hash'],
        model_data['url'],
    )
    if not ok:
        failed.append(model_data['model_name'])

if failed:
    print(f"\nFailed to download {len(failed)} file(s): {', '.join(failed)}")
    sys.exit(1)

print("\nAll models are downloaded and verified.")
