import { NextResponse, type NextRequest } from "next/server";

const publicPaths = new Set(["/anmelden", "/registrieren", "/passwort-vergessen"]);

function normalize(pathname: string): string {
  if (pathname.length > 1 && pathname.endsWith("/")) {
    return pathname.slice(0, -1);
  }
  return pathname;
}

export function proxy(request: NextRequest) {
  const pathname = normalize(request.nextUrl.pathname);
  if (publicPaths.has(pathname)) {
    return NextResponse.next();
  }

  const session = request.cookies.get("sessionid")?.value;
  if (!session) {
    return NextResponse.redirect(new URL("/anmelden", request.url));
  }

  if (pathname === "/") {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!accounts|_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};
