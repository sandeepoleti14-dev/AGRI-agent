import { GoogleGenAI } from "@google/genai";

import { verifyRecommendation } from "../verifier/verifier.js";

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

export async function visionAgentNode(state) {
  if (!state.visionDetection) {
    return { status: "vision_skipped" };
  }

  return { status: "vision_completed" };
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

export async function decisionAgentNode(state) {
  const response = await generateText(
    `
You are the Decision Agent of AGRI Agent.

You provide a cautious, evidence-based agricultural
recommendation.

Use ONLY information present in the supplied state.

Available information:

- Farmer question
- Farmer profile
- Vision result
- Weather data
- Agricultural knowledge evidence

Rules:

1. Do not invent facts.
2. Do not invent sources.
3. Do not invent weather conditions.
4. Do not claim certainty when evidence is insufficient.
5. Clearly distinguish observations from conclusions.
6. If evidence is insufficient, recommend obtaining
   additional information.
7. Prefer safe, practical agricultural actions.
8. For chemical treatment recommendations, avoid
   unsupported dosage instructions.
9. If the case may require an agricultural expert,
   clearly say so.

Return a concise recommendation that can be shown
to a farmer.
    `,
    JSON.stringify(
      {
        farmerPrompt: state.farmerPrompt,
        farmerProfile: state.farmerProfile,
        visionDetection: state.visionDetection,
        weatherData: state.weatherData,
        ragEvidence: state.ragEvidence,
      },
      null,
      2
    )
  );

  return {
    decision: response,
    status: "decision_completed",
  };
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