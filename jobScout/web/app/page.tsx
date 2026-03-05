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
  const [tag, setTag] = useState("");
  const [minScore, setMinScore] = useState(0);
  const [days, setDays] = useState(7);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    const r = await fetch(
      `/api/jobs?days=${days}&tag=${tag}&minScore=${minScore}&devOnly=1`,
      { cache: "no-store" },
    );
    const j = await r.json();
    setJobs(j.data ?? []);
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, [tag, days, minScore]);

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
          Role{" "}
          <select value={tag} onChange={(e) => setTag(e.target.value)}>
            <option value="">All</option>
            <option value="frontend">Front-End</option>
            <option value="webdev">Web Developer</option>
            <option value="fullstack">Full Stack</option>
            <option value="mobile">Mobile</option>
            <option value="data">Data Analyst</option>
          </select>
        </label>

        <label>
          Range{" "}
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
          >
            <option value={1}>Last 24h</option>
            <option value={3}>Last 3 days</option>
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
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
              </div>
              <div style={{ fontWeight: 800 }}>Score {job.score}</div>
            </div>
          </a>
        ))}

        {jobs.length === 0 && (
          <div style={{ opacity: 0.7, marginTop: 12 }}>
            No jobs found. Once ingestion writes into Supabase, this will
            populate.
          </div>
        )}
      </div>
    </main>
  );
}
