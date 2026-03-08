from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from backend.agents.cam_agent import run_cam_agent
from backend.agents.financial_agent import run_financial_agent
from backend.agents.ingestion_agent import run_ingestion_agent
from backend.agents.litigation_agent import run_litigation_agent
from backend.agents.research_agent import run_research_agent
from backend.agents.risk_agent import run_risk_agent


AGENT_WORKFLOW_SEQUENCE = [
    ("ingestion_agent", "Document Ingestion Agent"),
    ("financial_agent", "Financial Analysis Agent"),
    ("research_agent", "Research Agent"),
    ("litigation_agent", "Litigation Analysis Agent"),
    ("risk_agent", "Risk Scoring Agent"),
    ("cam_agent", "CAM Generator Agent"),
]


class WorkflowState(TypedDict, total=False):
    company: dict[str, Any]
    documents: list[dict[str, Any]]
    primary_insights: list[str]
    credit_officer_observations: str
    financial_metrics: dict[str, Any]
    research: dict[str, Any]
    litigation: dict[str, Any]
    risk: dict[str, Any]
    recommendation: dict[str, Any]
    reports: dict[str, str]


def build_workflow():
    graph = StateGraph(WorkflowState)

    graph.add_node("ingestion_agent", run_ingestion_agent)
    graph.add_node("financial_agent", run_financial_agent)
    graph.add_node("research_agent", run_research_agent)
    graph.add_node("litigation_agent", run_litigation_agent)
    graph.add_node("risk_agent", run_risk_agent)
    graph.add_node("cam_agent", run_cam_agent)

    graph.set_entry_point("ingestion_agent")
    graph.add_edge("ingestion_agent", "financial_agent")
    graph.add_edge("financial_agent", "research_agent")
    graph.add_edge("research_agent", "litigation_agent")
    graph.add_edge("litigation_agent", "risk_agent")
    graph.add_edge("risk_agent", "cam_agent")
    graph.add_edge("cam_agent", END)

    return graph.compile()


workflow = build_workflow()


def run_credit_workflow(state: WorkflowState) -> WorkflowState:
    return workflow.invoke(state)
