import os
import sys
import asyncio
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END

AGENT_DIR = Path(__file__).parent / "agent"
if str(AGENT_DIR) not in sys.path:
    sys.path.append(str(AGENT_DIR))

from state.state import SDRState  # type: ignore[reportMissingImports]
from nodes.call_llm import (  # type: ignore[reportMissingImports]
    discard_agent,
    fetch_crm_contacts,
    first_contact_agent,
    follow_up_agent,
    intent_agent,
    meet_agent,
)
from nodes.routing import crm_decision, status_decision  # type: ignore[reportMissingImports]

load_dotenv()
_ = os.environ.get("GROQ_API_KEY")

def create_graph():
    graph = StateGraph(SDRState)
    
    # Add nodes
    graph.add_node("fetch_crm_contacts", fetch_crm_contacts)
    graph.add_node("first_contact_agent", first_contact_agent)
    graph.add_node("intent_agent", intent_agent)
    graph.add_node("follow_up_agent", follow_up_agent)
    graph.add_node("meet_agent", meet_agent)
    graph.add_node("discard_agent", discard_agent)

    # Edge definition
    graph.add_edge(START, "fetch_crm_contacts")

    graph.add_conditional_edges(
        "fetch_crm_contacts",
        status_decision,
        {
            "first_contact": "first_contact_agent",
            "follow_up": "follow_up_agent",
            "analyze_intent": "intent_agent",
            "done": END,
        },
    )

    # Conditional routing after intent is analyzed
    graph.add_conditional_edges(
        "intent_agent",
        crm_decision,
        {
            "follow_up": "follow_up_agent",
            "schedule_meet": "meet_agent",
            "discard_lead": "discard_agent",
        }
    )
    
    graph.add_edge("follow_up_agent", END)
    graph.add_edge("meet_agent", END)
    graph.add_edge("first_contact_agent", END)
    graph.add_edge("discard_agent", END)
    
    return graph


def compile_graph(checkpointer: Any | None = None):
    graph = create_graph()
    if checkpointer is None:
        return graph.compile()
    return graph.compile(checkpointer=checkpointer)


def _message_content(message: BaseMessage | dict[str, Any]) -> str:
    if isinstance(message, BaseMessage):
        return str(message.content)
    return str(message.get("content", ""))


def _message_role(message: BaseMessage | dict[str, Any]) -> str:
    if isinstance(message, BaseMessage):
        return message.type
    role = str(message.get("role", "")).strip().lower()
    if role in {"assistant", "ai"}:
        return "ai"
    if role in {"human", "user"}:
        return "human"
    return role


def _last_assistant_message(messages: list[BaseMessage | dict[str, Any]]) -> str:
    for message in reversed(messages):
        if _message_role(message) == "ai":
            return _message_content(message)
    return ""


async def run_turn(initial_state: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    app = compile_graph()
    final_state = await app.ainvoke(initial_state, config=config or {})

    response_text = str(final_state.get("generated_response") or "").strip()
    if not response_text:
        response_text = _last_assistant_message(final_state.get("messages", []))

    return {
        "action": final_state.get("next_action", "wait"),
        "contact_status": final_state.get("contact_status", "new"),
        "user_intent": final_state.get("user_intent", "none"),
        "response_text": response_text,
        "intent_analysis": final_state.get("intent_analysis", {}),
    }

async def main():
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from psycopg_pool import AsyncConnectionPool

    connection_string = os.environ.get("POSTGRES_URI", "postgresql://user:password@localhost:5432/postgres")
    
    async with AsyncConnectionPool(
        connection_string,
        max_size=20,
        kwargs={"autocommit": True, "prepare_threshold": 0},
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        
        # NOTE: you need to call .setup() the first time to create tables
        awaits_setup = os.environ.get("SETUP_DB", "true").lower() == "true"
        if awaits_setup:
            await checkpointer.setup()

        app = compile_graph(checkpointer=checkpointer)
        
        # Run test
        config = {"configurable": {"thread_id": "test_sdr_thread"}}
        initial_state = {
            "lead_data": {
                "name": "Test Prospect",
                "role": "Diretor(a) de Operações",
                "company": "Empresa Exemplo",
                "sector": "Tecnologia",
                "company_size": "200",
                "location": "Curitiba",
                "public_context": "Empresa em crescimento e expansão regional",
            },
            "contact_status": "new",
            "user_intent": "none",
        }
        
        print("Starting graph...")
        async for event in app.astream(initial_state, config):
            for k, v in event.items():
                if k != "__end__":
                    print(f"Node output from {k}:")
                    print(v)
        
if __name__ == "__main__":
    asyncio.run(main())
