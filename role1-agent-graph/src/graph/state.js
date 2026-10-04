import { Annotation } from "@langchain/langgraph";

export const AgriState = Annotation.Root({
  farmerPrompt: Annotation({
    reducer: (_, next) => next,
    default: () => "",
  }),

  farmerProfile: Annotation({
    reducer: (_, next) => next,
    default: () => null,
  }),

  visionDetection: Annotation({
    reducer: (_, next) => next,
    default: () => null,
  }),

  weatherData: Annotation({
    reducer: (_, next) => next,
    default: () => null,
  }),

  ragEvidence: Annotation({
    reducer: (_, next) => next,
    default: () => [],
  }),

  selectedAgents: Annotation({
    reducer: (_, next) => next,
    default: () => [],
  }),

  decision: Annotation({
    reducer: (_, next) => next,
    default: () => null,
  }),

  verification: Annotation({
    reducer: (_, next) => next,
    default: () => null,
  }),

  needsEscalation: Annotation({
    reducer: (_, next) => next,
    default: () => false,
  }),

  messages: Annotation({
    reducer: (current, next) => [...current, ...next],
    default: () => [],
  }),

  status: Annotation({
    reducer: (_, next) => next,
    default: () => "started",
  }),

  errors: Annotation({
    reducer: (current, next) => [...current, ...next],
    default: () => [],
  }),
});