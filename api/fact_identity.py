"""
The two inputs of the identity of a person without an account, read from a request at the boundary of the programming interface (M9).

The address is the client of the request as uvicorn resolved it: behind the trusted proxy of `API_TRUSTED_PROXY_ADDRESSES`
the rightmost untrusted entry of X-Forwarded-For, otherwise the peer of the connection. The User-Agent is the text of the
header; a missing header is the empty text and repeated headers are joined in the order received with `, `
(`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-16, D-17). Nothing here logs either input.
"""

from fastapi import Request

from service.anonymous_voters import AnonymousVoterInput, build_anonymous_voter_input

USER_AGENT_SEPARATOR = ", "


def fetch_anonymous_voter_input(request: Request) -> AnonymousVoterInput:
    """Reads the address and the User-Agent of a request, refusing a request without a client IP address as a fault of the transport."""
    host = None if request.client is None else request.client.host
    return build_anonymous_voter_input(host, USER_AGENT_SEPARATOR.join(request.headers.getlist("user-agent")))
