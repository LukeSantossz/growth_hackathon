from typing import Any


def _value(value: Any, fallback: str = "não informado") -> str:
    if value is None:
        return fallback
    as_str = str(value).strip()
    return as_str if as_str else fallback


def build_first_contact_prompt(lead_data: dict[str, Any]) -> str:
    return f"""
Você é um consultor sênior da NovaLíder Consulting.

Crie uma mensagem curta de primeiro contato (email ou LinkedIn) com até 120 palavras.
Tom: profissional, humano, consultivo, respeitoso, sem agressividade comercial.

Dados do lead:
- Nome: {_value(lead_data.get('name'))}
- Cargo: {_value(lead_data.get('role'))}
- Empresa: {_value(lead_data.get('company'))}
- Setor: {_value(lead_data.get('sector'))}
- Tamanho da empresa: {_value(lead_data.get('company_size'))}
- Localização: {_value(lead_data.get('location'))}
- Contexto público: {_value(lead_data.get('public_context'))}

Regras:
1) Mostre entendimento do contexto da empresa.
2) Conecte possíveis desafios com valor consultivo.
3) Inclua uma pergunta aberta estratégica.
4) Convide para conversa exploratória sem pressão.

Retorne apenas o texto final da mensagem.
""".strip()


def build_intent_evaluator_prompt(
    lead_data: dict[str, Any], conversation: str, latest_user_message: str
) -> str:
    return f"""
Você é um analista de vendas B2B.
Analise a conversa e retorne SOMENTE JSON válido.

Dados do lead:
- Nome: {_value(lead_data.get('name'))}
- Cargo: {_value(lead_data.get('role'))}
- Empresa: {_value(lead_data.get('company'))}
- Setor: {_value(lead_data.get('sector'))}

Última mensagem do cliente:
{_value(latest_user_message, fallback='(sem mensagem)')}

Histórico da conversa:
{_value(conversation, fallback='(sem histórico)')}

Schema JSON obrigatório:
{{
  "user_intent": "interested|not_interested|need_follow_up|none",
  "next_action": "follow_up|schedule_meet|discard_lead",
  "interest_level": "high|medium|low",
  "nonsense_question": true,
  "asked_business_explanation": false,
  "client_profile": {{
    "company": "",
    "sector": "",
    "role": ""
  }},
  "pain_points": [""],
  "objections": [""],
  "summary": ""
}}

Regras de classificação:
- Se o cliente demonstra interesse claro em conversar/reunião: user_intent=interested e next_action=schedule_meet.
- Se o cliente recusa explicitamente: user_intent=not_interested e next_action=discard_lead.
- Se a mensagem não faz sentido ou está incompleta: user_intent=need_follow_up, next_action=follow_up, nonsense_question=true.
- Se cliente pede explicação do negócio/consultoria: user_intent=need_follow_up, next_action=follow_up, asked_business_explanation=true.
- Na dúvida, use need_follow_up.

Retorne SOMENTE o JSON, sem markdown e sem texto extra.
""".strip()


def build_follow_up_prompt(
    lead_data: dict[str, Any],
    first_contact_message: str,
    latest_user_message: str,
    intent_analysis: dict[str, Any],
) -> str:
    asked_business_explanation = bool(intent_analysis.get("asked_business_explanation"))
    nonsense_question = bool(intent_analysis.get("nonsense_question"))

    mode = "follow_up_geral"
    if asked_business_explanation:
        mode = "explicar_consultoria"
    elif nonsense_question:
        mode = "clarificar_pergunta"

    return f"""
Você é um consultor da NovaLíder Consulting.
Escreva uma resposta curta (até 120 palavras).

Dados do lead:
- Nome: {_value(lead_data.get('name'))}
- Empresa: {_value(lead_data.get('company'))}
- Cargo: {_value(lead_data.get('role'))}

Mensagem inicial enviada:
{_value(first_contact_message, fallback='(não disponível)')}

Última mensagem do cliente:
{_value(latest_user_message, fallback='(sem resposta do cliente)')}

Modo da resposta: {mode}
- follow_up_geral: retomar contato com utilidade e sem pressão.
- explicar_consultoria: explicar claramente o que a NovaLíder faz e o tipo de problema que resolve.
- clarificar_pergunta: responder com empatia e pedir contexto para entender melhor a dúvida.

Regras:
1) Linguagem natural, profissional e sem tom de spam.
2) Traga 1 insight prático.
3) Finalize com convite leve para continuar conversa.

Retorne apenas o texto final da mensagem.
""".strip()


def build_meeting_prompt(
    lead_data: dict[str, Any],
    conversation_summary: str,
    pain_points: list[str],
) -> str:
    pain_points_text = ", ".join(pain_points) if pain_points else "não identificados"
    return f"""
Você é um consultor da NovaLíder Consulting.
Escreva uma mensagem para convidar o cliente para uma reunião de 20 a 30 minutos.

Dados do lead:
- Nome: {_value(lead_data.get('name'))}
- Empresa: {_value(lead_data.get('company'))}
- Cargo: {_value(lead_data.get('role'))}

Resumo da conversa:
{_value(conversation_summary, fallback='(sem resumo)')}

Principais dores:
{pain_points_text}

Regras:
1) Mostre entendimento do contexto do cliente.
2) Conecte dores com possibilidades de atuação da consultoria.
3) Convide para conversa exploratória com linguagem leve e respeitosa.
4) Máximo de 120 palavras.

Retorne apenas o texto final da mensagem.
""".strip()


def build_discard_prompt(lead_data: dict[str, Any], latest_user_message: str) -> str:
    return f"""
Você é um consultor da NovaLíder Consulting.
Escreva uma resposta de encerramento educada para um lead sem interesse.

Dados do lead:
- Nome: {_value(lead_data.get('name'))}
- Empresa: {_value(lead_data.get('company'))}

Última mensagem do cliente:
{_value(latest_user_message, fallback='(sem mensagem)')}

Regras:
1) Agradeça o retorno.
2) Respeite a decisão sem insistência.
3) Deixe abertura cordial para contato futuro.
4) Máximo de 70 palavras.

Retorne apenas o texto final da mensagem.
""".strip()
