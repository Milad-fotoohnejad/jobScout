import { NextResponse } from "next/server";

type JobRow = {
  company: string;
  title: string;
  location: string | null;
  url: string;
  score: number | null;
  tags: string[] | null;
  last_seen_utc: string | null;
  excluded: boolean | null;
  description?: string | null;
  posted_at?: string | null;
};

const ROLE_KEYWORDS: Record<string, string[]> = {
  frontend: [
    "frontend",
    "front-end",
    "front end",
    "react",
    "next.js",
    "nextjs",
    "ui engineer",
    "web developer",
    "frontend engineer",
    "front-end developer",
    "software engineer, frontend",
    "software engineer frontend",
    "react developer",
  ],
  fullstack: [
    "full stack",
    "full-stack",
    "fullstack",
    "software engineer",
    "product engineer",
    "web developer",
  ],
  mobile: [
    "mobile",
    "react native",
    "ios",
    "android",
    "flutter",
    "mobile developer",
    "mobile engineer",
  ],
  all: [],
};

const SENIORITY_BLOCKLIST = [
  "senior staff",
  "staff",
  "principal",
  "director",
  "manager",
  "lead",
  "architect",
  "vp",
  "head of",
];

function textOf(job: JobRow) {
  return [
    job.title ?? "",
    job.company ?? "",
    job.location ?? "",
    ...(job.tags ?? []),
    job.description ?? "",
  ]
    .join(" ")
    .toLowerCase();
}

function matchesRole(job: JobRow, role: string) {
  const keywords = ROLE_KEYWORDS[role] ?? [];
  if (!keywords.length) return true;
  const haystack = textOf(job);
  return keywords.some((kw) => haystack.includes(kw));
}

function isTooSenior(job: JobRow) {
  const haystack = textOf(job);
  return SENIORITY_BLOCKLIST.some((kw) => haystack.includes(kw));
}

function isRemote(job: JobRow) {
  const haystack = textOf(job);
  return (
    haystack.includes("remote") ||
    haystack.includes("work from home") ||
    haystack.includes("distributed")
  );
}

function getEffectiveTimestamp(job: JobRow) {
  return new Date(job.posted_at ?? job.last_seen_utc ?? 0).getTime();
}

export async function GET(req: Request) {
  const url = new URL(req.url);

  const hours = Number(url.searchParams.get("hours") ?? "24");
  const minScore = Number(url.searchParams.get("minScore") ?? "4");
  const role = url.searchParams.get("role") ?? "frontend";
  const remoteOnly = url.searchParams.get("remoteOnly") === "1";
  const strictTitles = url.searchParams.get("strictTitles") !== "0";
  const excludeSenior = url.searchParams.get("excludeSenior") !== "0";
  const devOnly = url.searchParams.get("devOnly") !== "0";

  const supabaseUrl = process.env.SUPABASE_URL;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !serviceKey) {
    return NextResponse.json(
      { error: "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY" },
      { status: 500 }
    );
  }

  const since = new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();

  let query =
    `${supabaseUrl}/rest/v1/jobs` +
    `?select=company,title,location,url,score,tags,last_seen_utc,posted_at,excluded,description` +
    `&last_seen_utc=gte.${encodeURIComponent(since)}` +
    `&score=gte.${minScore}` +
    `&order=last_seen_utc.desc`;

  if (devOnly) query += `&excluded=eq.false`;

  const r = await fetch(query, {
    headers: {
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
    },
    cache: "no-store",
  });

  if (!r.ok) {
    const raw = await r.text();
    return NextResponse.json(
      { error: "Supabase query failed", status: r.status, raw },
      { status: 500 }
    );
  }

  const data = (await r.json()) as JobRow[];

  let filtered = data;

  if (strictTitles) {
    filtered = filtered.filter((job) => matchesRole(job, role));
  }

  if (excludeSenior) {
    filtered = filtered.filter((job) => !isTooSenior(job));
  }

  if (remoteOnly) {
    filtered = filtered.filter((job) => isRemote(job));
  }

  filtered = filtered.sort((a, b) => {
    const aTime = getEffectiveTimestamp(a);
    const bTime = getEffectiveTimestamp(b);

    if (bTime !== aTime) return bTime - aTime;
    return (b.score ?? -999) - (a.score ?? -999);
  });

  return NextResponse.json({ data: filtered });
}