import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "FoilBrief | Race Intelligence Workspace",
  description: "Fleet-relative post-race review workspace for SailGP performance analysts.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header>
          <Link className="brand" href="/">
            <span className="brand-copy">FoilBrief <small>Race Intelligence</small></span>
          </Link>
          <nav>
            <Link href="/#top-maneuvers">Review Queue</Link>
            <Link href="/maneuver/413">Demo 413</Link>
          </nav>
        </header>
        <main>{children}</main>
        <footer>
          Hackathon prototype for Ocean of Data Challenge: Foil Forward, featuring SailGP
          telemetry. Human analyst makes the final decision.
        </footer>
      </body>
    </html>
  );
}
