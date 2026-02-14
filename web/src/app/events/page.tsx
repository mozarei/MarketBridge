import Link from "next/link";

import { getEvents } from "@/lib/api";

import styles from "./page.module.css";

export default async function EventsPage() {
  const events = await getEvents(100);

  return (
    <main className={styles.page}>
      <div className={styles.headerRow}>
        <h1>Sync Events</h1>
        <Link href="/" className={styles.backLink}>
          Back Home
        </Link>
      </div>

      {events.length === 0 ? (
        <p className={styles.empty}>No events yet.</p>
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Created</th>
                <th>Type</th>
                <th>Status</th>
                <th>Item</th>
                <th>Job</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => (
                <tr key={event.id}>
                  <td>{event.id}</td>
                  <td>{event.created_at.replace("T", " ").replace("Z", " UTC")}</td>
                  <td>{event.event_type}</td>
                  <td>
                    <span className={`${styles.badge} ${styles[event.status]}`}>{event.status}</span>
                  </td>
                  <td>{event.item_id ?? "-"}</td>
                  <td className={styles.job}>{event.job_id ?? "-"}</td>
                  <td>{event.message ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
