import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load the Role 1 .env BEFORE importing the graph.
// The .env file is inside role1-agent-graph.
dotenv.config({
  path: path.join(__dirname, ".env"),
});

// Import the graph only after environment variables are loaded.
const { agriGraph } = await import(
  "./src/graph/graph.js"
);

const app = express();
const frontendUrl = process.env.FRONTEND_URL || "http://localhost:5173";
const allowedOrigins = new Set([
  frontendUrl,
  "http://localhost:5173",
  "http://127.0.0.1:5173",
  "http://localhost:3000",
  "http://127.0.0.1:3000",
]);

app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin || allowedOrigins.has(origin)) {
        callback(null, true);
        return;
      }

      callback(new Error("Not allowed by CORS"));
    },
    credentials: true,
  })
);
app.use(express.json());

app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    service: "AGRI Agent API",
  });
});

app.post("/api/analyze", async (req, res) => {
  try {
    const data = req.body || {};

    const farmerPrompt =
      data.farmerPrompt ||
      data.question ||
      "";

    if (!farmerPrompt.trim()) {
      return res.status(400).json({
        status: "error",
        error: "Farmer question is required.",
      });
    }

    const input = {
      farmerPrompt: farmerPrompt.trim(),

      farmerProfile:
        data.farmerProfile || null,

      visionDetection:
        data.visionDetection || null,

      weatherData:
        data.weatherData || null,

      ragEvidence:
        data.ragEvidence || [],
    };

    const config = {
      configurable: {
        thread_id:
          "frontend-" + Date.now(),
      },
    };

    const result =
      await agriGraph.invoke(
        input,
        config
      );

    return res.json({
      status: "success",
      result,
    });

  } catch (error) {
    console.error(
      "AGRI API error:",
      error
    );

    return res.status(500).json({
      status: "error",
      error: error.message,
    });
  }
});

const port = Number(process.env.PORT) || 5000;

app.listen(port, "0.0.0.0", () => {
  console.log(
    `🌱 AGRI Agent API running on http://localhost:${port}`
  );
});