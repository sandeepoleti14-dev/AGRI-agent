import { registerFarmerSupabase, loginFarmerSupabase } from "./src/tools/supabaseAuth.js";
import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import fs from "fs";
import os from "os";
import crypto from "crypto";
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
const { runRole3Auth } = await import(
  "./src/tools/toolAdapter.js"
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

function saveVisionImage(visionDetection) {
  if (visionDetection == null) {
    return { visionDetection: null, temporaryImagePath: null };
  }
  if (typeof visionDetection !== "object" || Array.isArray(visionDetection)) {
    throw new Error("Uploaded image data is invalid.");
  }

  const imageData =
    visionDetection.dataUrl ||
    visionDetection.imageData ||
    visionDetection.image_data ||
    visionDetection.base64;

  if (typeof imageData !== "string") {
    throw new Error("Uploaded image data is missing.");
  }

  const match = imageData.match(/^data:(image\/[a-zA-Z0-9.+-]+);base64,(.*)$/);

  if (!match) {
    throw new Error("Uploaded image data is invalid.");
  }

  const mimeType = match[1];
  if (!["image/png", "image/jpeg", "image/webp"].includes(mimeType)) {
    throw new Error("Only JPG, PNG, and WebP images are supported.");
  }

  const base64Data = match[2];
  if (!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(base64Data)) {
    throw new Error("Uploaded image encoding is invalid.");
  }
  const imageBuffer = Buffer.from(base64Data, "base64");
  if (imageBuffer.length === 0 || imageBuffer.length > 8 * 1024 * 1024) {
    throw new Error("Images must be greater than 0 bytes and no larger than 8 MB.");
  }
  const extension = mimeType === "image/png"
    ? "png"
    : mimeType === "image/jpeg"
      ? "jpg"
      : mimeType === "image/webp"
        ? "webp"
        : "png";
  const tempDir = path.join(os.tmpdir(), "agri-agent-images");
  fs.mkdirSync(tempDir, { recursive: true });
  const filePath = path.join(
    tempDir,
    `${Date.now()}-${crypto.randomUUID()}.${extension}`
  );

  fs.writeFileSync(filePath, imageBuffer);

  return {
    visionDetection: {
      fileName: visionDetection.fileName,
      mimeType,
      image_path: filePath,
    },
    temporaryImagePath: filePath,
  };
}

app.use(
  cors({
    origin: (origin, callback) => {
      const localDevelopmentOrigin =
        /^http:\/\/(localhost|127\.0\.0\.1):\d+$/.test(origin || "");
      if (!origin || allowedOrigins.has(origin) || localDevelopmentOrigin) {
        callback(null, true);
        return;
      }

      callback(new Error("Not allowed by CORS"));
    },
    credentials: true,
  })
);
app.use(express.json({ limit: "12mb" }));

app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    service: "AGRI Agent API",
  });
});

app.post("/api/auth/login", async (req, res) => {
  const { name, password } = req.body || {};
  if (typeof name !== "string" || !name.trim() ||
      typeof password !== "string" || !password) {
    return res.status(400).json({
      status: "error",
      error: "Farmer name and password are required.",
    });
  }

  try {
    const farmer = await loginFarmerSupabase(
      name.trim(),
      password
    );
    if (!farmer) {
      return res.status(401).json({
        status: "error",
        error: "Farmer name or password is incorrect.",
      });
    }
    return res.json({ status: "success", farmer });
  } catch (error) {
    console.error("Farmer login failed:", error);
    return res.status(500).json({
      status: "error",
      error: "Unable to sign in right now.",
    });
  }
});

app.post("/api/auth/register", async (req, res) => {
  const account = req.body || {};
  const requiredFields = [
    "name",
    "password",
    "crop",
    "soil_type",
    "planting_date",
    "place_name",
    "pincode",
  ];
  if (requiredFields.some(
    (field) => typeof account[field] !== "string" || !account[field].trim()
  )) {
    return res.status(400).json({
      status: "error",
      error: "All farmer profile fields are required.",
    });
  }

  if (account.password.length < 6) {
    return res.status(400).json({
      status: "error",
      error: "Password must contain at least 6 characters.",
    });
  }
  if (!/^\d{6}$/.test(account.pincode)) {
    return res.status(400).json({
      status: "error",
      error: "Please enter a valid 6-digit pincode.",
    });
  }

  try {
    const farmer = await registerFarmerSupabase(account);
    if (!farmer) {
      return res.status(409).json({
        status: "error",
        error: "An account with this farmer name already exists.",
      });
    }
    return res.status(201).json({ status: "success", farmer });
  } catch (error) {
    console.error("Farmer registration failed:", error);
    return res.status(500).json({
      status: "error",
      error: "Unable to create the farmer account right now.",
    });
  }
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

    const savedImage = saveVisionImage(
      data.visionDetection || null
    );
    const input = {
      farmerPrompt: farmerPrompt.trim(),

      farmerProfile:
        data.farmerProfile || null,

      visionDetection: savedImage.visionDetection,

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

    try {
      const result = await agriGraph.invoke(input, config);
      return res.json({
        status: "success",
        result,
      });
    } finally {
      if (savedImage.temporaryImagePath) {
        try {
          fs.unlinkSync(savedImage.temporaryImagePath);
        } catch (cleanupError) {
          console.error(
            "Failed to remove temporary crop image:",
            cleanupError
          );
        }
      }
    }

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

export default app;





