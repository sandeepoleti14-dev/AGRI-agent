/*
 * AGRI Agent — Role 1 Verifier
 *
 * The verifier checks whether the Decision Agent's
 * recommendation is sufficiently supported before
 * it reaches the farmer.
 */

/**
 * Verify the agricultural recommendation.
 *
 * @param {Object} state - Current AGRI Agent state
 * @returns {Object} verification result
 */
export function verifyRecommendation(state) {
  const problems = [];
  const warnings = [];

  /*
   * --------------------------------------------------
   * 1. Decision must exist
   * --------------------------------------------------
   */

  if (!state.decision) {
    problems.push("No recommendation was produced.");
  }

  /*
   * --------------------------------------------------
   * 2. Evidence check
   * --------------------------------------------------
   */

  const evidence = state.ragEvidence || [];

  if (evidence.length === 0) {
    warnings.push(
      "No agricultural knowledge evidence was provided."
    );
  }

  /*
   * --------------------------------------------------
   * 3. Vision confidence check
   * --------------------------------------------------
   */

  const vision = state.visionDetection;

  if (vision) {
    const confidence = Number(vision.confidence);

    if (!Number.isNaN(confidence) && confidence < 0.6) {
      warnings.push(
        "Vision detection confidence is low."
      );
    }
  }

  /*
   * --------------------------------------------------
   * 4. Weather consistency check
   * --------------------------------------------------
   */

  const weather = state.weatherData;

  if (weather) {
    const weatherText = JSON.stringify(weather).toLowerCase();
    const decisionText = String(state.decision).toLowerCase();

    const rainDetected =
      weatherText.includes("rain") ||
      weatherText.includes("rainy") ||
      weatherText.includes("precipitation");

    const sprayRecommended =
      decisionText.includes("spray") ||
      decisionText.includes("fungicide") ||
      decisionText.includes("pesticide");

    if (rainDetected && sprayRecommended) {
      warnings.push(
        "The recommendation involves spraying while rain conditions are present. Weather suitability must be checked carefully."
      );
    }
  }

  /*
   * --------------------------------------------------
   * 5. Determine verification status
   * --------------------------------------------------
   */

  if (problems.length > 0) {
    return {
      status: "failed",
      verified: false,
      problems,
      warnings,
      reason: "The recommendation is missing required information.",
    };
  }

  /*
   * Warnings do not automatically mean failure.
   * They indicate that additional caution is required.
   */

  if (warnings.length > 0) {
    return {
      status: "warning",
      verified: true,
      problems: [],
      warnings,
      reason:
        "Recommendation passed basic verification but requires caution.",
    };
  }

  return {
    status: "verified",
    verified: true,
    problems: [],
    warnings: [],
    reason:
      "Recommendation passed the available verification checks.",
  };
}