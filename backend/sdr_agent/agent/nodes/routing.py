from state.state import SDRState

def status_decision(state: SDRState):
    status = state.get("contact_status", "new")

    if status == "new":
        return "first_contact"
    if status == "contacted":
        return "follow_up"
    if status == "replied":
        return "analyze_intent"
    return "done"


def crm_decision(state: SDRState):
    analysis = state.get("intent_analysis") or {}
    analysis_next_action = analysis.get("next_action")
    if analysis_next_action in {"follow_up", "schedule_meet", "discard_lead"}:
        return analysis_next_action

    intent = state.get('user_intent', 'none')
    if intent == 'interested':
        return "schedule_meet"
    elif intent in {'need_follow_up', 'none'}:
        return "follow_up"
    else:
        return "discard_lead"

def check_reply(state: SDRState):
    status = state.get("contact_status")
    if status == "replied":
        return "analyze_intent"
    return "wait"
