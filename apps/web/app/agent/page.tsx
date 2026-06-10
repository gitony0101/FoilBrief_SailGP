import { AgentPanel } from "@/components/AgentPanel";
import { SafeCaveat } from "@/components/SafeCaveat";

export default function AgentPage() {
  return (
    <>
      <section className="page-heading">
        <div className="eyebrow">Safe, grounded coach support</div>
        <h1>Saga Coach</h1>
        <p>Ask Saga for a concise summary grounded only in the selected maneuver&apos;s audited local evidence. Every response follows the same evidence and safety rules.</p>
      </section>
      <SafeCaveat />
      <AgentPanel />
    </>
  );
}
