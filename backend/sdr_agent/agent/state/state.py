from typing import Literal, Dict, Any, Optional
from langgraph.graph import MessagesState

class SDRState(MessagesState):
    lead_data: Optional[Dict[str, Any]]
    contact_status: Literal[
        "new",
        "contacted",
        "replied",
        "follow_up_sent",
        "meeting_scheduled",
        "discarded",
    ]
    user_intent: Literal["interested", "not_interested", "need_follow_up", "none"]
    last_contact_date: Optional[str]
    next_action: Literal[
        "first_contact",
        "follow_up",
        "schedule_meet",
        "discard_lead",
        "wait",
        "done",
    ]
    intent_analysis: Optional[Dict[str, Any]]
    generated_response: Optional[str]
