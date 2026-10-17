import hashlib
import os

from mcp.server.fastmcp import FastMCP, Context

EMAIL = "25f1000753@ds.study.iitm.ac.in"

mcp = FastMCP(
    "IITM Exam Challenge",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    stateless_http=True,
    json_response=False,
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

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
