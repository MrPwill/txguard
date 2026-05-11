from crewai import Agent, Task, Crew, Process
import os
from langchain_openai import ChatOpenAI
from .tools.transaction_tools import get_transaction_detail, get_account_history, compute_velocity_stats, get_geographic_profile, get_rule_trigger_detail
from .tools.rag_tools import search_fraud_typologies, search_aml_regulations, get_similar_past_investigations
from .tools.compliance_tools import check_merchant_watchlist, get_counterparty_risk, compute_structuring_signals, check_ctr_threshold, check_kyc_status, search_sanctions_list, get_jurisdiction_rules, format_investigation_report

def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model=os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash"),
    )

def create_investigation_crew(alert_id: str, transaction_id: str):
    llm = _get_llm()
    transaction_analyst = Agent(
        role="Transaction Analyst",
        goal="Build a complete behavioral profile for the flagged account and transaction.",
        backstory=(
            "You are a forensic data analyst specializing in financial transaction behavior. "
            "You have access to the account's full transaction history and real-time risk signals. "
            "Your job is to surface the behavioral facts — no interpretation, just clear, accurate context "
            "that the other investigators will rely on."
        ),
        tools=[
            get_transaction_detail,
            get_account_history,
            compute_velocity_stats,
            get_geographic_profile,
            get_rule_trigger_detail
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    fraud_investigator = Agent(
        role="Fraud Pattern Investigator",
        goal="Match the behavioral context against known fraud and money laundering typologies to identify what type of scheme, if any, this transaction may represent.",
        backstory=(
            "You are a fraud intelligence specialist with deep knowledge of financial crime patterns "
            "— card testing, structuring/smurfing, account takeover, mule account activity, and social engineering fraud. "
            "You receive behavioral data from the Transaction Analyst and determine which known typologies are consistent with what you're seeing."
        ),
        tools=[
            search_fraud_typologies,
            check_merchant_watchlist,
            get_counterparty_risk,
            compute_structuring_signals
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    compliance_specialist = Agent(
        role="AML Compliance Specialist",
        goal="Assess the transaction against applicable AML, KYC, and regulatory reporting obligations. Identify whether a SAR or CTR threshold has been met.",
        backstory=(
            "You are a compliance expert trained in AML regulations across multiple jurisdictions. "
            "You translate raw risk signals and fraud patterns into regulatory obligations. "
            "You cite specific rules and thresholds with precision."
        ),
        tools=[
            search_aml_regulations,
            check_ctr_threshold,
            check_kyc_status,
            search_sanctions_list,
            get_jurisdiction_rules
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    risk_decision_officer = Agent(
        role="Chief Risk Decision Officer",
        goal="Synthesize all investigative findings into a final, auditable recommendation.",
        backstory=(
            "You are a senior risk decision officer. You receive fully formed assessments from a behavioral analyst, "
            "a fraud investigator, and a compliance specialist. Your job is to weigh all inputs with clear logic, "
            "assign a confidence level to your conclusion, and produce a final recommendation that could withstand regulatory scrutiny."
        ),
        tools=[
            get_similar_past_investigations,
            format_investigation_report
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    behavioral_analysis_task = Task(
        description=(
            f"Analyze the behavioral profile for transaction {transaction_id} (Alert {alert_id}). "
            "Use your tools to fetch the transaction details, account history, velocity stats, geographic profile, "
            "and rule triggers. Compile this into a comprehensive behavioral summary."
        ),
        expected_output="A detailed behavioral profile in JSON-like structure or clear summary text covering amount, velocity, geography, and rule triggers.",
        agent=transaction_analyst
    )

    pattern_investigation_task = Task(
        description=(
            "Review the behavioral profile provided by the Transaction Analyst. "
            "Use your tools to search fraud typologies, check merchant risk, and compute structuring signals. "
            "Identify any matching fraud typologies."
        ),
        expected_output="A structured assessment of fraud patterns, merchant risk flags, and typology matches.",
        agent=fraud_investigator
    )

    regulatory_assessment_task = Task(
        description=(
            "Review the fraud pattern assessment. Check CTR thresholds, KYC status, sanctions lists, "
            "and query AML regulations using your tools. Determine if a SAR filing is indicated."
        ),
        expected_output="A regulatory assessment summary including SAR indications, CTR triggers, KYC status, and sanctions hits.",
        agent=compliance_specialist
    )

    final_decision_task = Task(
        description=(
            "Synthesize the behavioral profile, fraud pattern assessment, and regulatory assessment. "
            "Check for similar past investigations. Write a final, executive-level investigation report "
            "recommending CLEAR, ESCALATE_TO_SAR, BLOCK_AND_HOLD, or MONITOR. Include confidence score, rationale, "
            "and evidence citations. Output must map to the InvestigationReport format."
        ),
        expected_output=(
            "A JSON string mapping to the InvestigationReport schema containing recommended_action, "
            "confidence_score, executive_summary, decision_rationale, key_risk_factors, mitigating_factors, "
            "evidence_citations, and next_actions."
        ),
        agent=risk_decision_officer
    )

    crew = Crew(
        agents=[
            transaction_analyst,
            fraud_investigator,
            compliance_specialist,
            risk_decision_officer,
        ],
        tasks=[
            behavioral_analysis_task,
            pattern_investigation_task,
            regulatory_assessment_task,
            final_decision_task,
        ],
        process=Process.sequential,
        memory=True,
        verbose=True,
        max_execution_time=120
    )
    
    return crew
