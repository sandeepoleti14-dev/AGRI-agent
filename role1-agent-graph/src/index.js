import "dotenv/config";

import { agriGraph } from "./graph/graph.js";

async function main() {
  console.log("\n🌱 AGRI Agent — Role 1 Test\n");

  const input = {
    farmerPrompt:
      "My tomato leaves are showing yellow spots. What should I do?",
    
    farmerProfile: {
      crop: "Tomato",
      soil_type: "Red Loam",
      place_name: "Avadi",
      state: "Tamil Nadu",
    },

    visionDetection: null,

    weatherData: null,

    ragEvidence: [
      {
        source: "Demo agricultural knowledge",
        topic: "Tomato leaf symptoms",
        information:
          "Yellowing leaves can have multiple causes and should be diagnosed using additional evidence.",
      },
    ],
  };

  const config = {
    configurable: {
      thread_id: "role1-test-001",
    },
  };

  try {
    const result = await agriGraph.invoke(input, config);

    console.log("====================================");
    console.log("AGRI AGENT RESULT");
    console.log("====================================");

    console.log("\nStatus:");
    console.log(result.status);

    console.log("\nDecision:");
    console.log(result.decision);

    console.log("\nVerification:");
    console.log(
      JSON.stringify(result.verification, null, 2)
    );

    console.log("\nEscalation:");
    console.log(result.needsEscalation);

    console.log("\n====================================");
    console.log("ROLE 1 GRAPH TEST COMPLETED");
    console.log("====================================\n");
  } catch (error) {
    console.error("\n❌ Role 1 test failed:\n");
    console.error(error);
  }
}

main();