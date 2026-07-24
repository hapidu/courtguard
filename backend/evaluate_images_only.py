"""Quick re-test of just the image folders after fixing the label logic."""
import os
import requests

API_BASE = "http://127.0.0.1:8000"
API_KEY = "courtguard-secret-2026"
TEST_DATA_DIR = os.path.expanduser("~/Desktop/courtguard_test_data")
HEADERS = {"x-api-key": API_KEY}

FOLDERS = {
    "real_images": "real",
    "fake_images": "fake",
}

correct = 0
total = 0

for folder_name, ground_truth in FOLDERS.items():
    folder_path = os.path.join(TEST_DATA_DIR, folder_name)
    for filename in sorted(os.listdir(folder_path)):
        filepath = os.path.join(folder_path, filename)
        with open(filepath, "rb") as f:
            files = {"file": (filename, f)}
            res = requests.post(f"{API_BASE}/analyze/image", headers=HEADERS, files=files, timeout=180)
        result = res.json()
        verdict = result["verdict"].lower()
        is_correct = verdict == ground_truth
        correct += is_correct
        total += 1
        print(f"{folder_name}/{filename}: predicted={verdict}, truth={ground_truth}, "
              f"conf={result['confidence_score']}% -> {'CORRECT' if is_correct else 'WRONG'}")

print(f"\nAccuracy: {correct}/{total} ({round(100*correct/total, 1)}%)")