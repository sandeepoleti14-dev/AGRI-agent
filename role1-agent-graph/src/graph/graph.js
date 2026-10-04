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
 * Router
 *   ↓
 * Required specialist agents
 *   ↓
 * Decision Agent
 *   ↓
 * Verifier
 *   ↓
 * END
 */

const workflow = new StateGraph(AgriState);


/*
 * Register nodes
 *
 * IMPORTANT:
 * Node names must not match state attributes.
 */

workflow.addNode(
  "master",
  masterAgentNode
);

workflow.addNode(
  "vision",
  visionAgentNode
);

workflow.addNode(
  "weather",
  weatherAgentNode
);

workflow.addNode(
  "rag",
  ragAgentNode
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
 * Master → Specialist Agents
 *
 * LangGraph can fan out to multiple agents.
 *
 * All selected branches eventually converge
 * on the Decision Agent.
 */

workflow.addConditionalEdges(
  "master",
  routeAfterMaster,
  {
    vision: "vision",
    weather: "weather",
    rag: "rag",
  }
);


/*
 * Specialist Agents → Decision Agent
 *
 * These edges create the fan-in point.
 *
 * LangGraph waits for the required upstream
 * branches before continuing.
 */

workflow.addEdge(
  "vision",
  "decisionAgent"
);

workflow.addEdge(
  "weather",
  "decisionAgent"
);

workflow.addEdge(
  "rag",
  "decisionAgent"
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
 * MemorySaver gives each conversation thread
 * persistent graph state during the running process.
 */

const checkpointer = new MemorySaver();


/*
 * Compile the graph.
 */

export const agriGraph = workflow.compile({
  checkpointer,
});