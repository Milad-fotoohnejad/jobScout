"use client";

import { useEffect, useState } from "react";

type Job = {
  company: string;
  title: string;
  location: string | null;
  url: string;
  score: number;
  tags: string[];
  last_seen_utc: string;
};

export default function Page() {
  const [role, setRole] = useState("frontend");
  const [hours, setHours] = useState(24);
  const [minScore, setMinScore] = useState(4);
  const [remoteOnly, setRemoteOnly] = useState(true);
  const [strictTitles, setStrictTitles] = useState(true);
  const [excludeSenior, setExcludeSenior] = useState(true);

  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);

    const qs = new URLSearchParams({
      hours: String(hours),
      role,
      minScore: String(minScore),
      remoteOnly: remoteOnly ? "1" : "0",
      strictTitles: strictTitles ? "1" : "0",
      excludeSenior: excludeSenior ? "1" : "0",
      devOnly: "1",
    });

    const r = await fetch(`/api/jobs?${qs.toString()}`, {
      cache: "no-store",
    });

    const j = await r.json();
    setJobs(j.data ?? []);
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, [role, hours, minScore, remoteOnly, strictTitles, excludeSenior]);

  return (
    <main
      style={{
        maxWidth: 1100,
        margin: "40px auto",
        padding: 16,
        fontFamily: "system-ui",
      }}
    >
      <h1 style={{ fontSize: 28, fontWeight: 800 }}>JobScout Dashboard</h1>

      <div
        style={{
          display: "flex",
          gap: 12,
          marginTop: 16,
          flexWrap: "wrap",
          alignItems: "center",
        }}
      >
        <label>
          Track{" "}
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="frontend">Frontend</option>
            <option value="fullstack">Full Stack</option>
            <option value="mobile">Mobile</option>
            <option value="all">All</option>
          </select>
        </label>

        <label>
          Freshness{" "}
          <select
            value={hours}
            onChange={(e) => setHours(Number(e.target.value))}
          >
            <option value={24}>Last 24h</option>
            <option value={48}>Last 48h</option>
            <option value={72}>Last 72h</option>
            <option value={168}>Last 7 days</option>
          </select>
        </label>

        <label>
          Min score{" "}
          <input
            type="number"
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            style={{ width: 90 }}
            min={-10}
            max={20}
          />
        </label>

        <label>
          <input
            type="checkbox"
            checked={remoteOnly}
            onChange={(e) => setRemoteOnly(e.target.checked)}
          />{" "}
          Remote only
        </label>

        <label>
          <input
            type="checkbox"
            checked={strictTitles}
            onChange={(e) => setStrictTitles(e.target.checked)}
          />{" "}
          Strong title match
        </label>

        <label>
          <input
            type="checkbox"
            checked={excludeSenior}
            onChange={(e) => setExcludeSenior(e.target.checked)}
          />{" "}
          Exclude senior/staff
        </label>

        <button
          onClick={load}
          disabled={loading}
          style={{
            padding: "6px 10px",
            border: "1px solid #ddd",
            borderRadius: 8,
          }}
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      <div style={{ marginTop: 20, display: "grid", gap: 10 }}>
        {jobs.map((job) => (
          <a
            key={job.url}
            href={job.url}
            target="_blank"
            rel="noreferrer"
            style={{
              border: "1px solid #e5e5e5",
              borderRadius: 12,
              padding: 14,
              textDecoration: "none",
              color: "inherit",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 12,
              }}
            >
              <div>
                <div style={{ fontWeight: 800 }}>{job.title}</div>
                <div style={{ opacity: 0.75 }}>
                  {job.company}
                  {job.location ? ` | ${job.location}` : ""}
                </div>
                <div style={{ fontSize: 12, opacity: 0.6 }}>
                  Tags: {job.tags?.join(", ")}
                </div>
                <div style={{ fontSize: 12, opacity: 0.6 }}>
                  Seen: {new Date(job.last_seen_utc).toLocaleString()}
                </div>
              </div>
              <div style={{ fontWeight: 800 }}>Score {job.score}</div>
            </div>
          </a>
        ))}

        {jobs.length === 0 && (
          <div style={{ opacity: 0.7, marginTop: 12 }}>
            No matching jobs found for the current filters.
          </div>
        )}
      </div>
    </main>
  );
}