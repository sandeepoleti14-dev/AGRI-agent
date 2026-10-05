import {
  StateGraph,
  START,
  END,
  MemorySaver,
} from "@langchain/langgraph";

import { AgriState } from "./state.js";

import {
  masterAgentNode,
  visionAgentNode,
  weatherAgentNode,
  ragAgentNode,
  decisionAgentNode,
  verifierNode,
} from "./nodes.js";

import {
  routeAfterMaster,
  shouldProceedToDecision,
  shouldEscalate,
} from "./router.js";

/*
 * AGRI Agent — Role 1
 *
 * Main LangGraph orchestration.
 *
 * Flow:
 *
 * START
 *   ↓
 * Master Agent
 *   ↓
 * Specialist Coordinator
 *   ├── Vision + RAG through Role 2
 *   └── Weather when required
 *   ↓
 * Decision Agent
 *   ↓
 * Verifier
 *   ↓
 * END
 *
 * The Specialist Coordinator is intentionally a
 * single fan-in point. This guarantees that the
 * Decision Agent receives the completed specialist
 * results only once.
 */

const workflow = new StateGraph(AgriState);

/*
 * Register main nodes.
 */

workflow.addNode(
  "master",
  masterAgentNode
);

workflow.addNode(
  "specialists",
  async (state) => {
    const selectedAgents = routeAfterMaster(state);

    let currentState = {
      ...state,
      selectedAgents,
    };

    /*
     * Run selected specialist agents sequentially.
     *
     * Role 2 performs Vision + RAG together, so
     * we call visionAgentNode() only once when
     * the Vision route is selected.
     */
    if (selectedAgents.includes("vision")) {
      const visionResult = await visionAgentNode(currentState);

      currentState = {
        ...currentState,
        ...visionResult,
      };
    }

    /*
     * If only RAG is required, Role 2 still needs
     * to provide the agricultural evidence.
     *
     * Our current Role 2 integration performs
     * Vision + RAG together, so the RAG route
     * also uses the Role 2 analysis.
     */
    if (
      selectedAgents.includes("rag") &&
      !selectedAgents.includes("vision")
    ) {
      const ragResult = await visionAgentNode(currentState);

      currentState = {
        ...currentState,
        ...ragResult,
      };
    }

    /*
     * Weather is currently an adapter placeholder.
     * When Role 3 is connected, this node will call
     * the real Weather Agent.
     */
    if (selectedAgents.includes("weather")) {
      const weatherResult = await weatherAgentNode(currentState);

      currentState = {
        ...currentState,
        ...weatherResult,
      };
    }

    return {
      selectedAgents: currentState.selectedAgents,
      visionDetection: currentState.visionDetection,
      ragEvidence: currentState.ragEvidence,
      weatherData: currentState.weatherData,
      status: "specialists_completed",
      errors: currentState.errors || [],
    };
  }
);

workflow.addNode(
  "decisionAgent",
  decisionAgentNode
);

workflow.addNode(
  "verifier",
  verifierNode
);

/*
 * START → Master
 */

workflow.addEdge(
  START,
  "master"
);

/*
 * Master → Specialist Coordinator
 *
 * The coordinator internally uses the existing
 * routeAfterMaster() function to determine which
 * specialists are required.
 */

workflow.addEdge(
  "master",
  "specialists"
);

/*
 * Specialist Coordinator → Decision Agent
 *
 * Decision runs only after the selected specialists
 * have completed.
 */

workflow.addConditionalEdges(
  "specialists",
  shouldProceedToDecision,
  {
    true: "decisionAgent",
    false: END,
  }
);

/*
 * Decision → Verifier
 */

workflow.addConditionalEdges(
  "decisionAgent",
  shouldProceedToDecision,
  {
    true: "verifier",
    false: END,
  }
);

/*
 * Verifier → END
 *
 * Whether verification passes or escalation is
 * required, the graph ends here.
 *
 * The verification result and escalation state
 * remain available in the final graph state.
 */

workflow.addConditionalEdges(
  "verifier",
  shouldEscalate,
  {
    true: END,
    false: END,
  }
);

/*
 * Checkpointer
 *
 * MemorySaver keeps graph state associated with
 * the conversation thread while the process runs.
 */

const checkpointer = new MemorySaver();

/*
 * Compile the graph.
 */

export const agriGraph = workflow.compile({
  checkpointer,
});