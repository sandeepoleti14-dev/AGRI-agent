import { HumanMessage, SystemMessage } from "@langchain/core/messages";
import { ChatOpenAI } from "@langchain/openai";

import { verifyRecommendation } from "../verifier/verifier.js";


/*
 * Real LLM used by the Master and Decision Agents.
 *
 * API key must be supplied through:
 *
 * OPENAI_API_KEY=...
 *
 * in the .env file.
 */

const model = new ChatOpenAI({
  model: "gpt-4o-mini",
  temperature: 0.1,
});


/*
 * MASTER AGENT
 *
 * Understands the farmer request and coordinates
 * the specialist agents.
 */

export async function masterAgentNode(state) {
  const prompt = state.farmerPrompt;

  if (!prompt || !prompt.trim()) {
    return {
      status: "error",
      errors: ["Farmer prompt is missing."],
    };
  }

  const response = await model.invoke([
    new SystemMessage(`
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
    `),

    new HumanMessage(prompt),
  ]);

  return {
    messages: [response],
    status: "master_completed",
  };
}


/*
 * VISION AGENT
 *
 * Role 1 only orchestrates Vision.
 * The actual Vision implementation belongs
 * to Role 2.
 */

export async function visionAgentNode(state) {
  if (!state.visionDetection) {
    return {
      status: "vision_skipped",
    };
  }

  return {
    status: "vision_completed",
  };
}


/*
 * WEATHER AGENT
 *
 * Role 1 only orchestrates Weather.
 * The actual Weather implementation belongs
 * to Role 3.
 */

export async function weatherAgentNode(state) {
  if (!state.weatherData) {
    return {
      status: "weather_skipped",
    };
  }

  return {
    status: "weather_completed",
  };
}


/*
 * RAG KNOWLEDGE AGENT
 *
 * Role 1 only orchestrates RAG.
 * The actual RAG implementation belongs
 * to Role 2.
 */

export async function ragAgentNode(state) {
  if (
    !state.ragEvidence ||
    state.ragEvidence.length === 0
  ) {
    return {
      status: "rag_skipped",
    };
  }

  return {
    status: "rag_completed",
  };
}


/*
 * DECISION AGENT
 *
 * Combines:
 *
 * - Farmer question
 * - Farmer profile
 * - Vision result
 * - Weather data
 * - RAG evidence
 *
 * The Decision Agent must not invent missing
 * information.
 */

export async function decisionAgentNode(state) {
  const response = await model.invoke([
    new SystemMessage(`
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
    `),

    new HumanMessage(
      JSON.stringify(
        {
          farmerPrompt: state.farmerPrompt,

          farmerProfile:
            state.farmerProfile,

          visionDetection:
            state.visionDetection,

          weatherData:
            state.weatherData,

          ragEvidence:
            state.ragEvidence,
        },
        null,
        2
      )
    ),
  ]);

  return {
    decision: response.content,
    status: "decision_completed",
  };
}


/*
 * VERIFIER
 *
 * Runs after the Decision Agent.
 */

export async function verifierNode(state) {
  const verification =
    verifyRecommendation(state);

  return {
    verification,

    needsEscalation:
      verification.status !== "verified",

    status:
      "verification_completed",
  };
}