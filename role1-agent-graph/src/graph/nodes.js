import { GoogleGenAI } from "@google/genai";

import { verifyRecommendation } from "../verifier/verifier.js";
import {
  runRole2Analysis,
  runRole3Analysis,
} from "../tools/toolAdapter.js";

const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
});

const MODEL = "gemini-3.5-flash-lite";

async function generateText(systemInstruction, userPrompt) {
  const response = await ai.models.generateContent({
    model: MODEL,
    contents: userPrompt,
    config: {
      systemInstruction,
      temperature: 0.1,
    },
  });

  return response.text || "";
}

export async function masterAgentNode(state) {
  const prompt = state.farmerPrompt;

  if (!prompt || !prompt.trim()) {
    return {
      status: "error",
      errors: ["Farmer prompt is missing."],
    };
  }

  const response = await generateText(
    `
You are the Master Agent of AGRI Agent.

Your job is to understand the farmer's request
and coordinate the specialist agents.

Available specialist agents:

1. Vision Agent
   - analyzes crop images

2. Weather Agent
   - provides weather and environmental information

3. RAG Knowledge Agent
   - retrieves trusted agricultural knowledge

4. Decision Agent
   - combines the available evidence

5. Verifier
   - checks the recommendation before it reaches
     the farmer

Important rules:

- Do not make the final agricultural diagnosis yourself.
- Do not invent agricultural evidence.
- Do not invent weather information.
- Do not invent sources.
- Keep the farmer's original question intact.
    `,
    prompt
  );

  return {
    messages: [response],
    status: "master_completed",
  };
}

/**
 * Role 2 performs the combined Vision + RAG analysis.
 */
export async function visionAgentNode(state) {
  try {
    const result = await runRole2Analysis({
      image_path: state.visionDetection?.image_path || null,
      crop: state.farmerProfile?.crop || null,
      language: "English",
      query: state.farmerPrompt,
    });

    if (!result) {
      return {
        status: "vision_failed",
        errors: ["Role 2 returned no result."],
      };
    }

    const visionDetection = {
      crop: result.crop,
      possible_disease: result.disease,
      confidence: result.confidence,
      observations: result.observations || [],
    };

    const ragEvidence = Array.isArray(result.evidence)
      ? result.evidence
      : [];

    return {
      visionDetection,
      ragEvidence,
      status: "role2_completed",
    };
  } catch (error) {
    return {
      status: "vision_failed",
      errors: [`Role 2 analysis failed: ${error.message}`],
    };
  }
}

export async function weatherAgentNode(state) {
  if (!state.weatherData) {
    return { status: "weather_skipped" };
  }

  return { status: "weather_completed" };
}

export async function ragAgentNode(state) {
  if (
    !state.ragEvidence ||
    state.ragEvidence.length === 0
  ) {
    return { status: "rag_skipped" };
  }

  return { status: "rag_completed" };
}

/**
 * Real Role 3 Decision Agent.
 *
 * Role 2 provides disease candidates and RAG evidence.
 * Role 3 combines them with weather and farmer profile.
 */
export async function decisionAgentNode(state) {
  try {
    const diseaseName =
      state.visionDetection?.possible_disease ||
      "Uncertain";

    const rawConfidence = state.visionDetection?.confidence;
    const confidence =
      rawConfidence === null || rawConfidence === undefined || rawConfidence === ""
        ? null
        : Number(rawConfidence);

    const observations =
      Array.isArray(state.visionDetection?.observations)
        ? state.visionDetection.observations
        : [];

    const candidates =
      confidence !== null &&
      Number.isFinite(confidence) &&
      !["uncertain", "unknown"].includes(diseaseName.toLowerCase())
        ? [
            {
              name: diseaseName,
              confidence_pct:
                confidence <= 1
                  ? confidence * 100
                  : confidence,
              visual_evidence:
                observations.length > 0
                  ? observations.join("; ")
                  : "No visual observations available.",
            },
          ]
        : [];

    const ragChunks = Array.isArray(state.ragEvidence)
      ? state.ragEvidence
      : [];

    const placeName =
      state.farmerProfile?.place_name || null;

    const lat =
      state.farmerProfile?.lat ?? null;

    const lon =
      state.farmerProfile?.lon ?? null;

    const role3Result = await runRole3Analysis({
      farmer_id:
        state.farmerProfile?.id ?? null,

      farmer_name:
        state.farmerProfile?.name ?? null,

      password:
        state.farmerProfile?.password ?? null,

      place_name: placeName,

      lat,
      lon,

      candidates,
      rag_chunks: ragChunks,
    });

    if (!role3Result) {
      return {
        status: "decision_failed",
        errors: ["Role 3 returned no result."],
      };
    }

    return {
      farmerProfile:
        role3Result.farmer_profile ||
        state.farmerProfile ||
        null,

      weatherData:
        role3Result.weather ||
        state.weatherData ||
        null,

      decision:
        role3Result.decision ||
        null,

      status: "decision_completed",
    };
  } catch (error) {
    return {
      status: "decision_failed",
      errors: [
        `Role 3 decision failed: ${error.message}`,
      ],
    };
  }
}

export async function verifierNode(state) {
  const verification = verifyRecommendation(state);

  return {
    verification,
    needsEscalation:
      verification.status !== "verified",
    status: "verification_completed",
  };
}
