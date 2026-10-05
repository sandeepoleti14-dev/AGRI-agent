import json
import sys
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai_disease.pipeline import analyze_crop


def main():
    raw_input = sys.stdin.read().strip()

    if not raw_input:
        print(json.dumps({
            "status": "error",
            "error": "No input received."
        }))
        return

    try:
        request = json.loads(raw_input)

        # Capture all Role 2 diagnostic logs so Node.js sees
        # only the final JSON response on stdout.
        captured_output = StringIO()

        with redirect_stdout(captured_output), redirect_stderr(captured_output):
            result = analyze_crop(
                image_path=request.get("image_path"),
                crop=request.get("crop"),
                language=request.get("language", "English"),
                query=request.get("query"),
            )

        print(json.dumps({
            "status": "success",
            "result": result,
        }, ensure_ascii=False))

    except Exception as error:
        print(json.dumps({
            "status": "error",
            "error": str(error),
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()