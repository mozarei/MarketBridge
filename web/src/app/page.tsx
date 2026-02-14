import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: "2rem", fontFamily: "system-ui, sans-serif" }}>
      <h1>Crosslist Admin</h1>
      <p style={{ marginTop: "0.5rem" }}>Backend is connected. Open the events feed:</p>
      <p style={{ marginTop: "1rem" }}>
        <Link href="/events">Go to Sync Events</Link>
      </p>
    </main>
  );
}
