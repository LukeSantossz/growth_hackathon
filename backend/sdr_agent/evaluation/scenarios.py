from copy import deepcopy


DATASET_NAME = "sdr-agent-full-interaction"
DATASET_DESCRIPTION = (
    "Avaliação do agente SDR cobrindo primeiro contato, follow-up, "
    "intenção do lead, descarte cordial e agendamento de reunião."
)


BASE_LEAD = {
    "name": "Mariana Lopes",
    "role": "Diretora de Operações",
    "company": "TecVerde Soluções Industriais",
    "sector": "Tecnologia para eficiência energética industrial",
    "company_size": "180",
    "location": "Curitiba, Brasil",
    "public_context": "Crescimento acelerado, expansão LATAM e novas lideranças intermediárias.",
}


FIRST_CONTACT_MESSAGE = (
    "Olá, Mariana! Vi que a TecVerde tem crescido com força e expandido para "
    "novos mercados. Como vocês estão equilibrando crescimento com alinhamento "
    "entre as lideranças?"
)


SCENARIOS = [
    {
        "id": "first_interaction",
        "description": "Primeiro contato com cliente novo",
        "inputs": {
            "lead_data": deepcopy(BASE_LEAD),
            "contact_status": "new",
            "user_intent": "none",
            "messages": [],
        },
        "expected": {
            "expected_action": "first_contact",
            "expected_contact_status": "contacted",
            "expected_flags": {},
        },
    },
    {
        "id": "follow_up",
        "description": "Follow-up após primeiro contato sem resposta",
        "inputs": {
            "lead_data": deepcopy(BASE_LEAD),
            "contact_status": "contacted",
            "user_intent": "none",
            "messages": [
                {"role": "assistant", "content": FIRST_CONTACT_MESSAGE},
            ],
        },
        "expected": {
            "expected_action": "follow_up",
            "expected_contact_status": "follow_up_sent",
            "expected_flags": {},
        },
    },
    {
        "id": "follow_up_nonsense_question",
        "description": "Cliente responde com pergunta sem sentido",
        "inputs": {
            "lead_data": deepcopy(BASE_LEAD),
            "contact_status": "replied",
            "user_intent": "none",
            "messages": [
                {"role": "assistant", "content": FIRST_CONTACT_MESSAGE},
                {"role": "user", "content": "?? xyz 123, não entendi nada ..."},
            ],
        },
        "expected": {
            "expected_action": "follow_up",
            "expected_contact_status": "follow_up_sent",
            "expected_flags": {"nonsense_question": True},
        },
    },
    {
        "id": "follow_up_business_explanation",
        "description": "Cliente pede explicação sobre o negócio",
        "inputs": {
            "lead_data": deepcopy(BASE_LEAD),
            "contact_status": "replied",
            "user_intent": "none",
            "messages": [
                {"role": "assistant", "content": FIRST_CONTACT_MESSAGE},
                {
                    "role": "user",
                    "content": "Pode explicar melhor o que a NovaLíder faz e como ajuda uma empresa como a nossa?",
                },
            ],
        },
        "expected": {
            "expected_action": "follow_up",
            "expected_contact_status": "follow_up_sent",
            "expected_flags": {"asked_business_explanation": True},
        },
    },
    {
        "id": "discard_lead",
        "description": "Cliente sem interesse, encerrar cordialmente",
        "inputs": {
            "lead_data": deepcopy(BASE_LEAD),
            "contact_status": "replied",
            "user_intent": "none",
            "messages": [
                {"role": "assistant", "content": FIRST_CONTACT_MESSAGE},
                {"role": "user", "content": "Obrigado, mas não temos interesse neste momento."},
            ],
        },
        "expected": {
            "expected_action": "discard_lead",
            "expected_contact_status": "discarded",
            "expected_flags": {},
        },
    },
    {
        "id": "schedule_meeting",
        "description": "Cliente interessado, enviar convite para reunião",
        "inputs": {
            "lead_data": deepcopy(BASE_LEAD),
            "contact_status": "replied",
            "user_intent": "none",
            "messages": [
                {"role": "assistant", "content": FIRST_CONTACT_MESSAGE},
                {
                    "role": "user",
                    "content": "Faz sentido para nós. Podemos marcar uma conversa na terça de manhã?",
                },
            ],
        },
        "expected": {
            "expected_action": "schedule_meet",
            "expected_contact_status": "meeting_scheduled",
            "expected_flags": {},
        },
    },
]
