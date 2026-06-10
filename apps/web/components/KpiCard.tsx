export function KpiCard({ value, label }: { value: string; label: string }) {
  return (
    <article className="kpi-card">
      <strong>{value}</strong>
      <span>{label}</span>
    </article>
  );
}
