import { NextResponse } from "next/server";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const days = Number(url.searchParams.get("days") ?? "7");
  const tag = url.searchParams.get("tag") ?? "";
  const minScore = Number(url.searchParams.get("minScore") ?? "0");

  const supabaseUrl = process.env.SUPABASE_URL!;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

  const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();

  let query =
    `${supabaseUrl}/rest/v1/jobs` +
    `?select=company,title,location,url,score,tags,last_seen_utc` +
    `&last_seen_utc=gte.${encodeURIComponent(since)}` +
    `&score=gte.${minScore}` +
    `&order=last_seen_utc.desc`;

  if (tag) query += `&tags=cs.{${encodeURIComponent(tag)}}`;

  const r = await fetch(query, {
    headers: {
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
    },
    cache: "no-store",
  });

  const data = await r.json();
  return NextResponse.json({ data });
}