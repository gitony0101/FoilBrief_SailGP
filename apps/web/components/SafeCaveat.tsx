import { SAFE_CAVEAT } from "@/lib/safety";

export function SafeCaveat() {
  return <aside className="caveat">{SAFE_CAVEAT}</aside>;
}
