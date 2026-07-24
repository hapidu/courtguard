"""
Batch accuracy evaluation script for CourtGuard.

Runs every file in the test_data folders through the live API and builds
an accuracy table you can paste straight into your dissertation's
Testing & Evaluation chapter.

USAGE:
    Make sure your backend server is running first (uvicorn ...).
    Then run this script from anywhere:

        python evaluate_accuracy.py

REQUIREMENTS:
    pip install requests
"""
import os
import requests
import time

API_BASE = "http://127.0.0.1:8000"
API_KEY = "courtguard-secret-2026"  # must match your backend's COURTGUARD_API_KEY

TEST_DATA_DIR = os.path.expanduser("~/Desktop/courtguard_test_data")

# Maps folder name -> (endpoint, ground_truth_label)
FOLDERS = {
    "real_images": ("/analyze/image", "real"),
    "fake_images": ("/analyze/image", "fake"),
    "real_audio": ("/analyze/audio", "real"),
    "fake_audio": ("/analyze/audio", "fake"),
    "real_video": ("/analyze/video", "real"),
    "fake_video": ("/analyze/video", "fake"),
}

HEADERS = {"x-api-key": API_KEY}


def test_file(endpoint, filepath):
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f)}
        response = requests.post(f"{API_BASE}{endpoint}", headers=HEADERS, files=files, timeout=180)
    response.raise_for_status()
    return response.json()


def main():
    results = []

    for folder_name, (endpoint, ground_truth) in FOLDERS.items():
        folder_path = os.path.join(TEST_DATA_DIR, folder_name)
        if not os.path.isdir(folder_path):
            print(f"Skipping missing folder: {folder_path}")
            continue

        files = sorted(os.listdir(folder_path))
        for filename in files:
            filepath = os.path.join(folder_path, filename)
            print(f"Testing {folder_name}/{filename} ...", end=" ", flush=True)

            start = time.time()
            try:
                result = test_file(endpoint, filepath)
                verdict = result["verdict"].lower()
                confidence = result["confidence_score"]
                correct = (verdict == ground_truth)
                elapsed = round(time.time() - start, 1)
                print(f"-> {verdict} ({confidence}%) [{'CORRECT' if correct else 'WRONG'}] ({elapsed}s)")

                results.append({
                    "folder": folder_name,
                    "file": filename,
                    "ground_truth": ground_truth,
                    "predicted": verdict,
                    "confidence": confidence,
                    "correct": correct,
                    "seconds": elapsed,
                })
            except Exception as e:
                print(f"-> ERROR: {e}")
                results.append({
                    "folder": folder_name,
                    "file": filename,
                    "ground_truth": ground_truth,
                    "predicted": "ERROR",
                    "confidence": None,
                    "correct": False,
                    "seconds": None,
                })

    # --- Print summary table ---
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    by_module = {}
    for r in results:
        module = r["folder"].split("_")[1]  # images / audio / video
        by_module.setdefault(module, {"correct": 0, "total": 0})
        by_module[module]["total"] += 1
        if r["correct"]:
            by_module[module]["correct"] += 1

    for module, stats in by_module.items():
        acc = round(100 * stats["correct"] / stats["total"], 1) if stats["total"] else 0
        print(f"{module.upper():10s}: {stats['correct']}/{stats['total']} correct ({acc}%)")

    total_correct = sum(1 for r in results if r["correct"])
    total = len(results)
    overall_acc = round(100 * total_correct / total, 1) if total else 0
    print(f"\nOVERALL: {total_correct}/{total} correct ({overall_acc}%)")

    # --- Write a markdown table file for your dissertation ---
    output_path = "accuracy_results.md"
    with open(output_path, "w") as f:
        f.write("# CourtGuard — Accuracy Evaluation Results\n\n")
        f.write("| Module | File | Ground Truth | Predicted | Confidence | Correct | Time (s) |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['folder']} | {r['file']} | {r['ground_truth']} | {r['predicted']} | "
                     f"{r['confidence']} | {'✅' if r['correct'] else '❌'} | {r['seconds']} |\n")

        f.write("\n## Summary by module\n\n")
        f.write("| Module | Correct | Total | Accuracy |\n")
        f.write("|---|---|---|---|\n")
        for module, stats in by_module.items():
            acc = round(100 * stats["correct"] / stats["total"], 1) if stats["total"] else 0
            f.write(f"| {module} | {stats['correct']} | {stats['total']} | {acc}% |\n")
        f.write(f"\n**Overall accuracy: {total_correct}/{total} ({overall_acc}%)**\n")

    print(f"\nFull results written to {output_path} — ready to paste into your dissertation.")


if __name__ == "__main__":
    main()