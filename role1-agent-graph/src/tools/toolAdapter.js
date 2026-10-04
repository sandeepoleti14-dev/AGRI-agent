/*
 * AGRI Agent — Role 1 Tool Adapter
 *
 * Role 1 does NOT own the actual Vision, Weather,
 * or RAG implementations.
 *
 * This adapter provides a clean interface through
 * which those implementations can be connected later.
 */

/**
 * Vision Agent adapter
 *
 * Role 2 will provide the actual implementation.
 */
export async function runVisionAgent(input) {
  /*
   * Temporary placeholder.
   *
   * Later this function will call the real Vision Agent.
   */

  if (!input) {
    return null;
  }

  return input;
}

/**
 * Weather Agent adapter
 *
 * Role 3 will provide the actual weather implementation.
 */
export async function runWeatherAgent(input) {
  /*
   * Temporary placeholder.
   *
   * Later this function will call the real Weather Agent.
   */

  if (!input) {
    return null;
  }

  return input;
}

/**
 * RAG Knowledge adapter
 *
 * Role 2 will provide the actual RAG implementation.
 */
export async function runRagAgent(input) {
  /*
   * Temporary placeholder.
   *
   * Later this function will call the real RAG system.
   */

  if (!input) {
    return [];
  }

  return Array.isArray(input) ? input : [input];
}

/**
 * Combined tool interface
 *
 * Role 1 can use this object without knowing
 * how the individual tools are implemented.
 */
export const agriTools = {
  vision: runVisionAgent,
  weather: runWeatherAgent,
  rag: runRagAgent,
};