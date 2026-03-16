import os
import json
import re
from typing import Any

from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage

from prompts.templates import (
    build_discard_prompt,
    build_first_contact_prompt,
    build_follow_up_prompt,
    build_intent_evaluator_prompt,
    build_meeting_prompt,
)
from state.state import SDRState

load_dotenv()
_ = os.environ.get("GROQ_API_KEY")


def _get_llm() -> ChatGroq:
    return ChatGroq(model=os.environ.get("GROQ_MODEL"), temperature=0.2)


def _message_role(message: BaseMessage | dict[str, Any]) -> str:
    if isinstance(message, BaseMessage):
        return message.type
    role = str(message.get("role", "")).strip().lower()
    if role in {"assistant", "ai"}:
        return "ai"
    if role in {"human", "user"}:
        return "human"
    return role


def _message_content(message: BaseMessage | dict[str, Any]) -> str:
    if isinstance(message, BaseMessage):
        return str(message.content)
    return str(message.get("content", ""))


def _conversation_to_text(messages: list[BaseMessage | dict[str, Any]]) -> str:
    lines: list[str] = []
    for message in messages:
        role = _message_role(message)
        content = _message_content(message)
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _latest_user_message(messages: list[BaseMessage | dict[str, Any]]) -> str:
    for message in reversed(messages):
        if _message_role(message) == "human":
            return _message_content(message)
    return ""


def _first_assistant_message(messages: list[BaseMessage | dict[str, Any]]) -> str:
    for message in messages:
        if _message_role(message) == "ai":
            return _message_content(message)
    return ""


def _parse_json(content: str) -> dict[str, Any]:
    try:
        data = json.loads(content)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", content)
    if not match:
        return {}

    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _normalize_intent_analysis(analysis: dict[str, Any], lead_data: dict[str, Any]) -> dict[str, Any]:
    valid_intents = {"interested", "not_interested", "need_follow_up", "none"}
    valid_actions = {"follow_up", "schedule_meet", "discard_lead"}

    intent = str(analysis.get("user_intent", "none")).strip().lower()
    if intent not in valid_intents:
        intent = "none"

    next_action = str(analysis.get("next_action", "")).strip().lower()
    if next_action not in valid_actions:
        if intent == "interested":
            next_action = "schedule_meet"
        elif intent == "not_interested":
            next_action = "discard_lead"
        else:
            next_action = "follow_up"

    client_profile = analysis.get("client_profile") or {}
    if not isinstance(client_profile, dict):
        client_profile = {}

    normalized = {
        "user_intent": intent,
        "next_action": next_action,
        "interest_level": str(analysis.get("interest_level", "low")).strip().lower(),
        "nonsense_question": bool(analysis.get("nonsense_question", False)),
        "asked_business_explanation": bool(analysis.get("asked_business_explanation", False)),
        "client_profile": {
            "company": str(client_profile.get("company") or lead_data.get("company") or ""),
            "sector": str(client_profile.get("sector") or lead_data.get("sector") or ""),
            "role": str(client_profile.get("role") or lead_data.get("role") or ""),
        },
        "pain_points": [str(item) for item in (analysis.get("pain_points") or []) if str(item).strip()],
        "objections": [str(item) for item in (analysis.get("objections") or []) if str(item).strip()],
        "summary": str(analysis.get("summary", "")).strip(),
    }
    return normalized

async def fetch_crm_contacts(state: SDRState):
    lead_data = state.get("lead_data") or {}
    contact_status = state.get("contact_status") or "new"
    return {
        "lead_data": lead_data,
        "contact_status": contact_status,
    }

async def first_contact_agent(state: SDRState):
    llm = _get_llm()
    lead_data = state.get("lead_data") or {}
    system_prompt = build_first_contact_prompt(lead_data)
    msg = llm.invoke([{"role": "system", "content": system_prompt}])
    response_text = str(msg.content).strip()
    return {
        "messages": [AIMessage(content=response_text)],
        "generated_response": response_text,
        "contact_status": "contacted",
        "next_action": "first_contact",
    }

async def intent_agent(state: SDRState):
    llm = _get_llm()
    lead_data = state.get("lead_data") or {}
    messages = state.get("messages", [])
    latest_user_message = _latest_user_message(messages)
    conversation_text = _conversation_to_text(messages)

    system_prompt = build_intent_evaluator_prompt(
        lead_data=lead_data,
        conversation=conversation_text,
        latest_user_message=latest_user_message,
    )
    msg = llm.invoke([{"role": "system", "content": system_prompt}])

    parsed = _parse_json(str(msg.content))
    normalized = _normalize_intent_analysis(parsed, lead_data)

    return {
        "user_intent": normalized["user_intent"],
        "intent_analysis": normalized,
        "next_action": normalized["next_action"],
    }

async def follow_up_agent(state: SDRState):
    llm = _get_llm()
    lead_data = state.get("lead_data") or {}
    messages = state.get("messages", [])
    latest_user_message = _latest_user_message(messages)
    first_contact_message = _first_assistant_message(messages)
    intent_analysis = state.get("intent_analysis") or {}

    system_prompt = build_follow_up_prompt(
        lead_data=lead_data,
        first_contact_message=first_contact_message,
        latest_user_message=latest_user_message,
        intent_analysis=intent_analysis,
    )
    msg = llm.invoke([{"role": "system", "content": system_prompt}])

    response_text = str(msg.content).strip()
    return {
        "messages": [AIMessage(content=response_text)],
        "generated_response": response_text,
        "contact_status": "follow_up_sent",
        "next_action": "follow_up",
    }

async def meet_agent(state: SDRState):
    llm = _get_llm()
    lead_data = state.get("lead_data") or {}
    intent_analysis = state.get("intent_analysis") or {}

    system_prompt = build_meeting_prompt(
        lead_data=lead_data,
        conversation_summary=str(intent_analysis.get("summary", "")).strip(),
        pain_points=[
            str(item) for item in (intent_analysis.get("pain_points") or []) if str(item).strip()
        ],
    )
    msg = llm.invoke([{"role": "system", "content": system_prompt}])

    response_text = str(msg.content).strip()
    return {
        "messages": [AIMessage(content=response_text)],
        "generated_response": response_text,
        "contact_status": "meeting_scheduled",
        "next_action": "schedule_meet",
    }


async def discard_agent(state: SDRState):
    llm = _get_llm()
    lead_data = state.get("lead_data") or {}
    messages = state.get("messages", [])
    latest_user_message = _latest_user_message(messages)

    system_prompt = build_discard_prompt(
        lead_data=lead_data,
        latest_user_message=latest_user_message,
    )
    msg = llm.invoke([{"role": "system", "content": system_prompt}])

    response_text = str(msg.content).strip()
    return {
        "messages": [AIMessage(content=response_text)],
        "generated_response": response_text,
        "contact_status": "discarded",
        "next_action": "discard_lead",
    }
