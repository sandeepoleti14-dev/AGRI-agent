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

  try {
    let lat = input.lat ?? input.farmerProfile?.lat ?? null;
    let lon = input.lon ?? input.farmerProfile?.lon ?? null;

    if (lat == null || lon == null) {
      const placeName =
        input.place_name ||
        input.farmerProfile?.place_name ||
        "";

      if (!placeName) {
        return { status: "weather unavailable" };
      }

      const geocodeResponse = await fetch(
        "https://nominatim.openstreetmap.org/search?" +
          new URLSearchParams({
            q: placeName,
            format: "json",
            limit: "1",
          }),
        {
          headers: {
            "User-Agent": "AGRI-Agent/1.0",
            Accept: "application/json",
          },
        }
      );

      if (!geocodeResponse.ok) {
        return { status: "weather unavailable" };
      }

      const places = await geocodeResponse.json();

      if (!places.length) {
        return { status: "weather unavailable" };
      }

      lat = Number(places[0].lat);
      lon = Number(places[0].lon);
    }

    const weatherResponse = await fetch(
      "https://api.open-meteo.com/v1/forecast?" +
        new URLSearchParams({
          latitude: String(lat),
          longitude: String(lon),
          current:
            "temperature_2m,relative_humidity_2m,precipitation,weather_code",
          hourly:
            "temperature_2m,relative_humidity_2m,precipitation_probability",
          forecast_days: "3",
          timezone: "auto",
        })
    );

    if (!weatherResponse.ok) {
      return { status: "weather unavailable" };
    }

    const data = await weatherResponse.json();
    const current = data.current || {};
    const hourly = data.hourly || {};

    const humidity = hourly.relative_humidity_2m || [];
    const rainProbability =
      hourly.precipitation_probability || [];

    return {
      status: "ok",
      current: {
        temperature_c: current.temperature_2m ?? null,
        humidity_pct: current.relative_humidity_2m ?? null,
        precipitation_mm: current.precipitation ?? null,
        weather_code: current.weather_code ?? null,
      },
      forecast_72h: {
        max_humidity_pct: humidity.length
          ? Math.max(...humidity)
          : null,
        max_rain_probability_pct: rainProbability.length
          ? Math.max(...rainProbability)
          : null,
        hourly_humidity: humidity.slice(0, 72),
        hourly_rain_probability:
          rainProbability.slice(0, 72),
      },
    };
  } catch (error) {
    return {
      status: "weather unavailable",
      error: error.message,
    };
  }
}
/**
 * Combined tool interface
 */
export const agriTools = {
  role2: runRole2Analysis,
  role3: runRole3Analysis,
  weather: runWeatherAgent,
};