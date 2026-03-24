"use client";

import { useEffect, useMemo, useState } from "react";
import type { CSSProperties, ReactNode } from "react";

type Job = {
  company: string;
  title: string;
  location: string | null;
  url: string;
  score: number;
  tags: string[];
  last_seen_utc: string;
  posted_at?: string | null;
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
    try {
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
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [role, hours, minScore, remoteOnly, strictTitles, excludeSenior]);

  const summary = useMemo(() => {
    if (loading) return "Refreshing high-fit opportunities...";
    if (jobs.length === 0) return "No matching jobs found for the current filters.";
    if (jobs.length === 1) return "1 matching role found.";
    return `${jobs.length} matching roles found.`;
  }, [jobs.length, loading]);

  return (
    <main
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top, rgba(59,130,246,0.14), transparent 28%), #050816",
        color: "#E5E7EB",
        fontFamily:
          'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        padding: "32px 20px 64px",
      }}
    >
      <div
        style={{
          maxWidth: 1180,
          margin: "0 auto",
        }}
      >
        <section
          style={{
            border: "1px solid rgba(255,255,255,0.10)",
            background: "rgba(10, 14, 30, 0.82)",
            backdropFilter: "blur(10px)",
            borderRadius: 24,
            padding: 24,
            boxShadow: "0 20px 60px rgba(0,0,0,0.35)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: 16,
              flexWrap: "wrap",
              alignItems: "flex-start",
            }}
          >
            <div>
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "6px 10px",
                  borderRadius: 999,
                  background: "rgba(59,130,246,0.12)",
                  border: "1px solid rgba(59,130,246,0.25)",
                  color: "#93C5FD",
                  fontSize: 12,
                  fontWeight: 700,
                  letterSpacing: 0.4,
                  marginBottom: 14,
                }}
              >
                JOBSCOUT
              </div>

              <h1
                style={{
                  fontSize: 36,
                  lineHeight: 1.1,
                  margin: 0,
                  fontWeight: 800,
                  color: "#F9FAFB",
                }}
              >
                JobScout Dashboard
              </h1>

              <p
                style={{
                  margin: "12px 0 0",
                  fontSize: 15,
                  color: "#9CA3AF",
                  maxWidth: 720,
                }}
              >
                Fresh, high-signal roles prioritized for speed, relevance, and
                early application advantage.
              </p>
            </div>

            <button
              onClick={load}
              disabled={loading}
              style={{
                border: "1px solid rgba(255,255,255,0.14)",
                background: loading
                  ? "rgba(255,255,255,0.06)"
                  : "linear-gradient(135deg, #2563EB, #1D4ED8)",
                color: "#FFFFFF",
                borderRadius: 14,
                padding: "12px 16px",
                fontWeight: 700,
                cursor: loading ? "not-allowed" : "pointer",
                minWidth: 120,
                boxShadow: loading ? "none" : "0 8px 20px rgba(37,99,235,0.35)",
              }}
            >
              {loading ? "Refreshing..." : "Refresh"}
            </button>
          </div>

          <div
            style={{
              marginTop: 22,
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: 14,
            }}
          >
            <Field label="Track">
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                style={inputStyle}
              >
                <option value="frontend">Frontend</option>
                <option value="fullstack">Full Stack</option>
                <option value="mobile">Mobile</option>
                <option value="all">All</option>
              </select>
            </Field>

            <Field label="Freshness">
              <select
                value={hours}
                onChange={(e) => setHours(Number(e.target.value))}
                style={inputStyle}
              >
                <option value={24}>Last 24 hours</option>
                <option value={72}>Last 3 days</option>
              </select>
            </Field>

            <Field label="Min score">
              <input
                type="number"
                value={minScore}
                onChange={(e) => setMinScore(Number(e.target.value))}
                min={-10}
                max={20}
                style={inputStyle}
              />
            </Field>
          </div>

          <div
            style={{
              marginTop: 14,
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
              gap: 14,
            }}
          >
            <ToggleCard
              label="Remote only"
              checked={remoteOnly}
              onChange={setRemoteOnly}
            />

            <ToggleCard
              label="Strong title match"
              checked={strictTitles}
              onChange={setStrictTitles}
            />

            <ToggleCard
              label="Exclude senior/staff"
              checked={excludeSenior}
              onChange={setExcludeSenior}
            />
          </div>

          <div
            style={{
              marginTop: 18,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: 12,
              flexWrap: "wrap",
            }}
          >
            <div style={{ color: "#9CA3AF", fontSize: 14 }}>{summary}</div>

            <div
              style={{
                display: "flex",
                gap: 8,
                flexWrap: "wrap",
              }}
            >
              <Badge text={`Track: ${labelForRole(role)}`} />
              <Badge text={hours === 24 ? "24h window" : "3-day window"} />
              <Badge text={`Score ≥ ${minScore}`} />
            </div>
          </div>
        </section>

        <section
          style={{
            marginTop: 22,
            display: "grid",
            gap: 14,
          }}
        >
          {jobs.map((job) => (
            <a
              key={job.url}
              href={job.url}
              target="_blank"
              rel="noreferrer"
              style={{
                textDecoration: "none",
                color: "inherit",
              }}
            >
              <article
                style={{
                  border: "1px solid rgba(255,255,255,0.10)",
                  background:
                    "linear-gradient(180deg, rgba(16,22,43,0.95), rgba(8,12,25,0.95))",
                  borderRadius: 22,
                  padding: 20,
                  boxShadow: "0 10px 35px rgba(0,0,0,0.25)",
                  transition: "transform 160ms ease, border-color 160ms ease",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: 16,
                    flexWrap: "wrap",
                  }}
                >
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div
                      style={{
                        fontSize: 22,
                        fontWeight: 800,
                        color: "#F9FAFB",
                        lineHeight: 1.2,
                        wordBreak: "break-word",
                      }}
                    >
                      {job.title}
                    </div>

                    <div
                      style={{
                        marginTop: 8,
                        fontSize: 15,
                        color: "#C7D2FE",
                      }}
                    >
                      {job.company}
                      {job.location ? (
                        <span style={{ color: "#94A3B8" }}>
                          {" "}
                          • {job.location}
                        </span>
                      ) : null}
                    </div>

                    <div
                      style={{
                        marginTop: 6,
                        fontSize: 13,
                        color: "#94A3B8",
                      }}
                    >
                      {job.posted_at
                        ? `Published ${formatDateTime(job.posted_at)}`
                        : `Last seen ${formatDateTime(job.last_seen_utc)}`}
                    </div>

                    <div
                      style={{
                        marginTop: 14,
                        display: "flex",
                        gap: 8,
                        flexWrap: "wrap",
                      }}
                    >
                      {(job.tags ?? []).map((tag) => (
                        <span
                          key={`${job.url}-${tag}`}
                          style={{
                            padding: "6px 10px",
                            borderRadius: 999,
                            fontSize: 12,
                            fontWeight: 700,
                            color: "#BFDBFE",
                            background: "rgba(37,99,235,0.12)",
                            border: "1px solid rgba(37,99,235,0.24)",
                          }}
                        >
                          {tag}
                        </span>
                      ))}

                      <span
                        style={{
                          padding: "6px 10px",
                          borderRadius: 999,
                          fontSize: 12,
                          fontWeight: 700,
                          color: "#D1D5DB",
                          background: "rgba(255,255,255,0.05)",
                          border: "1px solid rgba(255,255,255,0.10)",
                        }}
                      >
                        {job.posted_at
                          ? `Posted ${formatSeen(job.posted_at)}`
                          : `Seen ${formatSeen(job.last_seen_utc)}`}
                      </span>
                    </div>
                  </div>

                  <div
                    style={{
                      minWidth: 110,
                      display: "flex",
                      justifyContent: "flex-end",
                    }}
                  >
                    <div
                      style={{
                        borderRadius: 18,
                        padding: "12px 14px",
                        background: scoreBackground(job.score),
                        border: "1px solid rgba(255,255,255,0.10)",
                        textAlign: "center",
                        minWidth: 96,
                      }}
                    >
                      <div
                        style={{
                          fontSize: 11,
                          letterSpacing: 0.6,
                          textTransform: "uppercase",
                          color: "#CBD5E1",
                          fontWeight: 700,
                        }}
                      >
                        Match Score
                      </div>
                      <div
                        style={{
                          marginTop: 6,
                          fontSize: 28,
                          fontWeight: 800,
                          color: "#FFFFFF",
                          lineHeight: 1,
                        }}
                      >
                        {job.score}
                      </div>
                    </div>
                  </div>
                </div>
              </article>
            </a>
          ))}

          {!loading && jobs.length === 0 && (
            <div
              style={{
                border: "1px dashed rgba(255,255,255,0.14)",
                borderRadius: 22,
                padding: 28,
                background: "rgba(255,255,255,0.03)",
                color: "#9CA3AF",
                textAlign: "center",
              }}
            >
              No matching jobs found for the current filters.
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 8,
      }}
    >
      <span
        style={{
          fontSize: 13,
          fontWeight: 700,
          color: "#9CA3AF",
          letterSpacing: 0.2,
        }}
      >
        {label}
      </span>
      {children}
    </label>
  );
}

function ToggleCard({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 12,
        width: "100%",
        padding: "14px 16px",
        borderRadius: 16,
        border: checked
          ? "1px solid rgba(59,130,246,0.45)"
          : "1px solid rgba(255,255,255,0.10)",
        background: checked
          ? "rgba(37,99,235,0.12)"
          : "rgba(255,255,255,0.04)",
        color: "#E5E7EB",
        cursor: "pointer",
        minHeight: 58,
      }}
    >
      <span style={{ fontSize: 14, fontWeight: 700 }}>{label}</span>
      <span
        style={{
          width: 42,
          height: 24,
          borderRadius: 999,
          background: checked ? "#2563EB" : "rgba(255,255,255,0.12)",
          position: "relative",
          transition: "all 160ms ease",
          flexShrink: 0,
        }}
      >
        <span
          style={{
            position: "absolute",
            top: 3,
            left: checked ? 21 : 3,
            width: 18,
            height: 18,
            borderRadius: "50%",
            background: "#FFFFFF",
            transition: "all 160ms ease",
          }}
        />
      </span>
    </button>
  );
}

function Badge({ text }: { text: string }) {
  return (
    <span
      style={{
        padding: "6px 10px",
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 700,
        color: "#CBD5E1",
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      {text}
    </span>
  );
}

function labelForRole(role: string) {
  if (role === "frontend") return "Frontend";
  if (role === "fullstack") return "Full Stack";
  if (role === "mobile") return "Mobile";
  return "All";
}

function formatSeen(value: string) {
  const date = new Date(value);
  const now = Date.now();
  const diffMs = now - date.getTime();
  const diffHours = Math.max(0, Math.floor(diffMs / (1000 * 60 * 60)));

  if (diffHours < 1) return "just now";
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

function formatDateTime(value: string) {
  const date = new Date(value);
  return date.toLocaleString([], {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function scoreBackground(score: number) {
  if (score >= 8) {
    return "linear-gradient(135deg, rgba(16,185,129,0.25), rgba(5,150,105,0.18))";
  }
  if (score >= 5) {
    return "linear-gradient(135deg, rgba(59,130,246,0.22), rgba(37,99,235,0.16))";
  }
  return "linear-gradient(135deg, rgba(107,114,128,0.22), rgba(75,85,99,0.14))";
}

const inputStyle: CSSProperties = {
  width: "100%",
  borderRadius: 14,
  border: "1px solid rgba(255,255,255,0.10)",
  background: "rgba(255,255,255,0.04)",
  color: "#F9FAFB",
  padding: "12px 14px",
  fontSize: 14,
  outline: "none",
};