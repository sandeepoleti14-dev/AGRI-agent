import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const projectRoot = path.resolve(__dirname, "../../../");

const role2BridgePath = path.join(
  projectRoot,
  "integration",
  "role2_bridge.py"
);

const role3BridgePath = path.join(
  projectRoot,
  "integration",
  "role3_bridge.py"
);

const pythonExecutable =
  process.env.PYTHON_EXECUTABLE ||
  process.env.PYTHON ||
  process.env.PYTHON3 ||
  (process.platform === "win32"
    ? "python.exe"
    : "python3");

function callPythonBridge(bridgePath, input, bridgeName) {
  return new Promise((resolve, reject) => {
    const python = spawn(
      pythonExecutable,
      [bridgePath],
      {
        cwd: projectRoot,
      }
    );

    let stdout = "";
    let stderr = "";

    python.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    python.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    python.on("error", (error) => {
      reject(error);
    });

    python.on("close", (code) => {
      if (code !== 0) {
        reject(
          new Error(
            `${bridgeName} failed with code ${code}: ${
              stderr || "Unknown error"
            }`
          )
        );
        return;
      }

      try {
        const lines = stdout
          .split(/\r?\n/)
          .map((line) => line.trim())
          .filter(Boolean);
        const payload = lines.at(-1) || stdout.trim();
        const response = JSON.parse(payload);

        if (response.status === "error") {
          reject(
            new Error(
              response.error ||
                `${bridgeName} returned an error.`
            )
          );
          return;
        }

        resolve(response.result);
      } catch (error) {
        reject(
          new Error(
            `Invalid response from ${bridgeName}: ${error.message}\n${stdout}`
          )
        );
      }
    });

    python.stdin.write(JSON.stringify(input));
    python.stdin.end();
  });
}

/**
 * Role 2 combined Vision + RAG analysis
 */
export async function runRole2Analysis(input) {
  if (!input) {
    return null;
  }

  return callPythonBridge(
    role2BridgePath,
    input,
    "Role 2 bridge"
  );
}

/**
 * Role 3 tools + Decision Agent
 *
 * Provides:
 * - farmer profile
 * - weather
 * - final decision
 */
export async function runRole3Analysis(input) {
  if (!input) {
    return null;
  }

  return callPythonBridge(
    role3BridgePath,
    input,
    "Role 3 bridge"
  );
}

export async function runRole3Auth(action, input) {
  return callPythonBridge(
    role3BridgePath,
    { ...input, action },
    "Role 3 bridge"
  );
}

/**
 * Weather adapter
 */
export async function runWeatherAgent(input) {
  if (!input) {
    return null;
  }

  return runRole3Analysis(input);
}

/**
 * Combined tool interface
 */
export const agriTools = {
  role2: runRole2Analysis,
  role3: runRole3Analysis,
  weather: runWeatherAgent,
};