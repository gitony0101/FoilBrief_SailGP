const unsafePatterns = [
  /caus(?:e|ed|al)/i,
  /prov(?:e|ed)/i,
  /optim(?:al|ize)/i,
  /guarantee/i,
  /precise.*seconds?/i,
  /autonom/i,
  /control[- ]command/i,
  /set (?:the )?(?:helm|foil|wing|trim) to/i,
  /best possible/i,
];

export const SAFE_REFUSAL =
  "FoilBrief cannot make causal or control-command claims from this dataset. It can summarize fleet-relative review evidence for human analyst review.";

export const WEATHER_ATTRIBUTION_REFUSAL =
  "FoilBrief cannot attribute the maneuver loss to weather. It can show environment context alongside fleet-relative telemetry evidence for human review.";

export const SAFE_CAVEAT =
  "Queue score only orders review candidates. Coach review should rely on visible telemetry evidence and human analyst judgment.";

export function requestsUnsafeClaim(prompt: string) {
  return unsafePatterns.some((pattern) => pattern.test(prompt));
}

export function requestsWeatherAttribution(prompt: string) {
  return /weather/i.test(prompt) && /caus(?:e|ed|al)|attribute|explain|responsible/i.test(prompt);
}

export function containsUnsafeGeneratedLanguage(answer: string) {
  return [
    /caused/i,
    /proved/i,
    /optimal/i,
    /guaranteed/i,
    /exact time loss/i,
    /exact seconds lost/i,
    /true gybe/i,
    /true tack/i,
    /autonomous decision/i,
    /control command/i,
    /weather caused/i,
    /caused by weather/i,
    /loss attribution/i,
    /attribute(?:d|s|ing)? .{0,40} loss/i,
    /set (?:the )?(?:helm|foil|wing|trim) to/i,
  ].some((pattern) => pattern.test(answer));
}

export function safeSystemPrompt() {
  return [
    "You are the FoilBrief Hybrid Coach Analyst Agent.",
    "Use only the provided audited local evidence.",
    "Describe findings as estimated, fleet-relative review signals.",
    "Treat environment data as supplementary review context, never as causal attribution.",
    "Say telemetry suggests and worth analyst review.",
    "Refer to the Coach Loss Card and state that the human analyst decides.",
    "Do not make causal, certainty, optimization, control, or autonomous-sailing claims.",
  ].join(" ");
}
