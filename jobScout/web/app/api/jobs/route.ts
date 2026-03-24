import { NextResponse } from "next/server";

export async function GET(req: Request) {
  const url = new URL(req.url);

  const days = Number(url.searchParams.get("days") ?? "7");
  const tag = url.searchParams.get("tag") ?? "";
  const minScore = Number(url.searchParams.get("minScore") ?? "0");

  // Default behavior: dev-only (hide excluded). Set devOnly=0 to see everything.
  const devOnly = url.searchParams.get("devOnly") !== "0";

  const supabaseUrl = process.env.SUPABASE_URL;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  console.log("[/api/jobs] params", { days, tag, minScore, devOnly });
  console.log("[/api/jobs] env", {
    hasSupabaseUrl: !!supabaseUrl,
    hasServiceKey: !!serviceKey,
    supabaseUrl,
  });

  if (!supabaseUrl || !serviceKey) {
    console.error("[/api/jobs] Missing env vars");
    return NextResponse.json(
      { error: "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY" },
      { status: 500 }
    );
  }

  const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();

  let query =
    `${supabaseUrl}/rest/v1/jobs` +
    `?select=company,title,location,url,score,tags,last_seen_utc,excluded` +
    `&last_seen_utc=gte.${encodeURIComponent(since)}` +
    `&score=gte.${minScore}` +
    `&order=score.desc,last_seen_utc.desc`;

  if (tag) query += `&tags=cs.{${encodeURIComponent(tag)}}`;
  if (devOnly) query += `&excluded=eq.false`;

  console.log("[/api/jobs] since", since);
  console.log("[/api/jobs] query", query);

  const r = await fetch(query, {
    headers: {
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
    },
    cache: "no-store",
  });

  console.log("[/api/jobs] response status", r.status, r.statusText);

  const text = await r.text();
  console.log("[/api/jobs] raw response", text.slice(0, 1000));

  let data;
  try {
    data = JSON.parse(text);
  } catch (e) {
    console.error("[/api/jobs] JSON parse failed", e);
    return NextResponse.json(
      { error: "Supabase returned non-JSON response", raw: text },
      { status: 500 }
    );
  }

  console.log("[/api/jobs] rows returned", Array.isArray(data) ? data.length : "not-array");

  return NextResponse.json({ data });
}