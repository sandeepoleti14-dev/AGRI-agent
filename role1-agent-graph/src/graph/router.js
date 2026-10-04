/*
 * AGRI Agent — Role 1 Router
 *
 * Determines which specialist agents are required
 * for the farmer's request.
 */

export function routeAfterMaster(state) {
  const prompt = (state.farmerPrompt || "").toLowerCase();

  const routes = [];

  /*
   * Vision
   *
   * Vision is selected when image analysis is already
   * available from the frontend / Vision Agent.
   */
  if (state.visionDetection) {
    routes.push("vision");
  }

  /*
   * Weather
   */
  const weatherKeywords = [
    "weather",
    "rain",
    "rainfall",
    "humidity",
    "temperature",
    "heat",
    "cold",
    "wind",
    "irrigation",
    "water",
    "spray",
    "pesticide",
    "fungicide",
    "fertilizer",
  ];

  if (
    weatherKeywords.some((keyword) =>
      prompt.includes(keyword)
    )
  ) {
    routes.push("weather");
  }

  /*
   * RAG / Agricultural Knowledge
   *
   * Most agricultural questions require trusted
   * agricultural knowledge, so RAG is the default.
   */
  const ragKeywords = [
    "disease",
    "pest",
    "insect",
    "fungus",
    "fungal",
    "leaf",
    "leaves",
    "yellow",
    "spot",
    "spots",
    "blight",
    "deficiency",
    "nutrient",
    "crop",
    "plant",
    "seed",
    "soil",
    "fertilizer",
    "treatment",
    "control",
    "growth",
    "symptom",
    "symptoms",
  ];

  if (
    ragKeywords.some((keyword) =>
      prompt.includes(keyword)
    )
  ) {
    routes.push("rag");
  }

  /*
   * Agricultural questions should normally have
   * trusted knowledge available.
   */
  if (routes.length === 0) {
    routes.push("rag");
  }

  /*
   * Remove duplicates.
   */
  const uniqueRoutes = [...new Set(routes)];

  return uniqueRoutes;
}

/*
 * Save the selected agents into state.
 */
export function saveSelectedAgents(state) {
  return {
    selectedAgents: state.selectedAgents || [],
  };
}

/*
 * Decision Agent should only run after the
 * specialist stage has completed.
 */
export function shouldProceedToDecision(state) {
  if (state.status === "error") {
    return false;
  }

  return true;
}

/*
 * Determine whether the final result needs escalation.
 */
export function shouldEscalate(state) {
  if (!state.decision) {
    return true;
  }

  if (!state.verification) {
    return true;
  }

  if (
    state.verification.status === "failed"
  ) {
    return true;
  }

  return Boolean(state.needsEscalation);
}