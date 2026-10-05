import json
import subprocess
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ROLE1_DIR = PROJECT_ROOT / "role1-agent-graph"


app = Flask(__name__)
CORS(app)


def run_role1(payload):
    process = subprocess.run(
        ["npm", "start"],
        cwd=ROLE1_DIR,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        shell=True,
    )

    if process.returncode != 0:
        raise RuntimeError(
            process.stderr
            or process.stdout
            or "Role 1 failed."
        )

    return process.stdout


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "AGRI Agent API"
    })


@app.post("/api/analyze")
def analyze():
    try:
        data = request.get_json(silent=True) or {}

        farmer_prompt = (
            data.get("farmerPrompt")
            or data.get("question")
            or ""
        ).strip()

        farmer_profile = data.get(
            "farmerProfile"
        ) or {}

        if not farmer_prompt:
            return jsonify({
                "status": "error",
                "error": "Farmer question is required."
            }), 400

        payload = {
            "farmerPrompt": farmer_prompt,
            "farmerProfile": farmer_profile,
            "visionDetection": data.get(
                "visionDetection"
            ),
            "weatherData": data.get(
                "weatherData"
            ),
            "ragEvidence": data.get(
                "ragEvidence",
                []
            ),
        }

        output = run_role1(payload)

        return jsonify({
            "status": "success",
            "role1_output": output
        })

    except Exception as error:
        return jsonify({
            "status": "error",
            "error": str(error)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )