import { NextRequest, NextResponse } from "next/server";

const apiOrigin = process.env.API_ORIGIN ?? "http://backend:8000";

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

async function proxy(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const target = new URL(`/media/${path.map(encodeURIComponent).join("/")}`, apiOrigin);
  target.search = request.nextUrl.search;

  const upstream = await fetch(target, {
    method: request.method,
    headers: { accept: request.headers.get("accept") ?? "image/*" },
    redirect: "manual",
    cache: "no-store",
  });

  const headers = new Headers();
  const type = upstream.headers.get("content-type");
  if (type) {
    headers.set("content-type", type);
  }
  headers.set("cache-control", "private, max-age=3600");

  return new NextResponse(upstream.status === 204 ? null : upstream.body, {
    status: upstream.status,
    headers,
  });
}

export const GET = proxy;
export const HEAD = proxy;
