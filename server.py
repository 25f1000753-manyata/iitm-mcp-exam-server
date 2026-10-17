
import hashlib
import os

import uvicorn
from mcp.server.fastmcp import FastMCP, Context

EMAIL = "25f1000753@ds.study.iitm.ac.in"

mcp = FastMCP(
    "IITM Exam Challenge",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def solve_challenge(ctx: Context) -> str:
    """Return the hash for the challenge in the current HTTP request headers."""
    request = ctx.request_context.request
    challenge = request.headers.get("x-exam-challenge")

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    return hashlib.sha256(
        f"{challenge}:{EMAIL}".encode("utf-8")
    ).hexdigest()[:16]


class AcceptCompatibilityMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("path") == "/mcp":
            headers = list(scope.get("headers", []))
            accept = next(
                (v.decode("latin-1") for k, v in headers
                 if k.lower() == b"accept"),
                "",
            )
            if ("application/json" not in accept.lower() or "text/event-stream" not in accept.lower()):
                headers = [
                    (k, v) for k, v in headers
                    if k.lower() != b"accept"
                ]
                headers.append((
                    b"accept",
                    b"application/json, text/event-stream",
                ))
                scope = dict(scope)
                scope["headers"] = headers

        await self.app(scope, receive, send)


if __name__ == "__main__":
    app = AcceptCompatibilityMiddleware(mcp.streamable_http_app())
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )
