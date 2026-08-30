from google import genai
from config import settings
from schemas.models import AgentQuery, AgentResponse, Asset, RiskScore, PriorityItem
from services.facility_service import Facility

_client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

SYSTEM_PROMPT = """You are THERMOS Decision Agent, a professional heat-response intelligence assistant for one facility.

You explain and recommend based ONLY on the structured data given to you below.
You must NEVER invent temperatures, risk scores, costs, or outcomes not present in the data.

FORMATTING RULES (always follow):
- Use short paragraphs, never one long block of text.
- Use markdown: **bold** for key terms, bullet points for lists, numbered steps for actions.
- If comparing zones, use a short bulleted list, one zone per line.
- Keep answers under 120 words unless the user asks for a detailed report.

SCOPE RULES:
- You only know about this facility's assets, risk scores, priorities, and recommended actions — nothing else.
- If asked about anything outside this facility (other cities, general chit-chat, unrelated topics),
  reply briefly and redirect: state plainly that it's outside your scope, then offer to help with
  facility risk instead. Do not just say "the data doesn't contain X" — be conversational but firm.

DATA DISTINCTIONS:
- "Observed" data comes from FortyGuard's thermal intelligence — treat as factual.
- "Calculated" risk/priority scores come from THERMOS's deterministic engine — explain, don't second-guess.
- "Recommended actions" are suggestions for a human facility manager — never phrase them as decisions already made.
"""


def _build_context(
    facility: Facility, assets: list[Asset], risks: list[RiskScore], priorities: list[PriorityItem]
) -> str:
    lines = [
        f"FACILITY: {facility.name} ({facility.location.city}, {facility.location.state}, {facility.location.country})",
        "",
        "ASSETS, RISK, AND PRIORITY:",
    ]
    risk_by_id = {r.asset_id: r for r in risks}
    priority_by_id = {p.asset_id: p for p in priorities}

    for asset in assets:
        risk = risk_by_id.get(asset.id)
        priority = priority_by_id.get(asset.id)
        if not risk or not priority:
            continue
        lines.append(
            f"- {asset.name} (id: {asset.id}): risk {risk.score}/100 ({risk.level}), "
            f"criticality {int(asset.criticality * 100)}%, priority rank #{priority.rank}. "
            f"Top drivers: hazard {risk.drivers.hazard}, exposure {risk.drivers.exposure}, "
            f"vulnerability {risk.drivers.vulnerability}, persistence {risk.drivers.persistence}. "
            f"Reason for priority: {priority.reason} "
            f"Recommended action: {priority.recommended_action}"
        )
    return "\n".join(lines)


def ask_agent(
    query: AgentQuery,
    facility: Facility,
    assets: list[Asset],
    risks: list[RiskScore],
    priorities: list[PriorityItem],
) -> AgentResponse:
    if _client is None:
        return AgentResponse(
            answer="AI agent is not configured (missing GEMINI_API_KEY). "
                   "Numerical risk and priority data above is still fully computed and reliable.",
            grounded_on=[a.id for a in assets],
        )

    context = _build_context(facility, assets, risks, priorities)
    user_message = f"{context}\n\nQuestion: {query.question}"

    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{SYSTEM_PROMPT}\n\n{user_message}",
    )

    return AgentResponse(
        answer=response.text,
        grounded_on=[a.id for a in assets],
    )