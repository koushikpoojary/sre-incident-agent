import sys
import os
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)


# ============================================================
# AGENT IMPORTS
# ============================================================

from agents.triage_agent import triage_incident, load_alerts
from agents.diagnostic_agent import diagnose_incident, load_json
from agents.remediation_agent import create_remediation_plan


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="SRE Incident Agent",
    description="Governed multi-agent SRE incident triage and remediation system",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# APPROVAL STATE
# ============================================================

# Stores approval decisions while the API is running.
# Each action has its own approval state.
approval_state = {}


# ============================================================
# INCIDENT STATE
# ============================================================

incident_state = {
    "status": "INVESTIGATING"
}


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": "SRE Incident Agent",
        "status": "running",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# ALERTS
# ============================================================

@app.get("/alerts")
def get_alerts():

    alerts = load_alerts()

    return {
        "count": len(alerts),
        "alerts": alerts
    }


# ============================================================
# INCIDENT
# ============================================================

@app.get("/incident")
def get_incident():

    alerts = load_alerts()

    logs = load_json("logs.json")

    deployments = load_json("deployments.json")


    # --------------------------------------------------------
    # TRIAGE AGENT
    # --------------------------------------------------------

    triage = triage_incident(alerts)


    # --------------------------------------------------------
    # DIAGNOSTIC AGENT
    # --------------------------------------------------------

    diagnosis = diagnose_incident(
        alerts,
        logs,
        deployments
    )


    # --------------------------------------------------------
    # REMEDIATION AGENT
    # --------------------------------------------------------

    remediation = create_remediation_plan(
        alerts,
        logs,
        deployments
    )


    # ========================================================
    # APPLY APPROVAL STATE
    # ========================================================

    for action in remediation.get(
        "recommended_actions",
        []
    ):

        action_name = action.get(
            "action",
            ""
        )


        # ----------------------------------------------------
        # HIGH-RISK ACTION
        # ----------------------------------------------------

        if action.get(
            "requires_human_approval",
            False
        ):

            stored = approval_state.get(
                action_name
            )


            if stored:

                action["approval_status"] = stored.get(
                    "approval_status",
                    "PENDING"
                )

                action["human_approval"] = stored.get(
                    "human_approval",
                    "REQUIRED"
                )

                action["execution"] = stored.get(
                    "execution",
                    "BLOCKED"
                )

            else:

                action["approval_status"] = "PENDING"

                action["human_approval"] = "REQUIRED"

                action["execution"] = "BLOCKED"


        # ----------------------------------------------------
        # LOW-RISK ACTION
        # ----------------------------------------------------

        else:

            action["approval_status"] = "APPROVED"

            action["human_approval"] = "NOT REQUIRED"

            action["execution"] = "SIMULATED"


    # ========================================================
    # INCIDENT STATUS
    # ========================================================

    incident_status = incident_state.get(
        "status",
        "INVESTIGATING"
    )


    # If at least one HIGH-risk action has been approved,
    # show that remediation approval has occurred.

    high_risk_actions = [
        action
        for action in remediation.get(
            "recommended_actions",
            []
        )
        if action.get(
            "requires_human_approval",
            False
        )
    ]


    approved_high_risk_actions = [
        action
        for action in high_risk_actions
        if action.get(
            "approval_status"
        ) == "APPROVED"
    ]


    if approved_high_risk_actions:

        incident_status = "REMEDIATION APPROVED"


    # ========================================================
    # RETURN COMPLETE INCIDENT
    # ========================================================

    return {

        "incident": triage,

        "diagnosis": diagnosis,

        "remediation": remediation,

        "status": incident_status,

        "agents": {

            "alert_ingestion": "COMPLETED",

            "triage": "COMPLETED",

            "diagnostic": "COMPLETED",

            "remediation": "COMPLETED",

            "safety_gate": "COMPLETED",

            "rca": "COMPLETED"

        }

    }


# ============================================================
# INCIDENT TIMELINE
# ============================================================

@app.get("/timeline")
def get_timeline():

    return {

        "incident": "INC-001",

        "timeline": [

            {
                "timestamp": "2026-09-10T10:25:00",
                "event": (
                    "Deployment v2.4.1 released "
                    "to payment-api"
                ),
                "type": "deployment"
            },

            {
                "timestamp": "2026-09-10T10:30:00",
                "event": (
                    "Memory usage exceeded 90%"
                ),
                "type": "alert",
                "severity": "P2"
            },

            {
                "timestamp": "2026-09-10T10:31:00",
                "event": (
                    "payment-api pod restarted"
                ),
                "type": "alert",
                "severity": "P1"
            },

            {
                "timestamp": "2026-09-10T10:32:00",
                "event": (
                    "HTTP 500 error rate "
                    "increased to 35%"
                ),
                "type": "alert",
                "severity": "P1"
            },

            {
                "timestamp": "2026-09-10T10:33:00",
                "event": (
                    "Triage Agent correlated "
                    "3 alerts into INC-001"
                ),
                "type": "agent"
            },

            {
                "timestamp": "2026-09-10T10:34:00",
                "event": (
                    "Diagnostic Agent identified "
                    "likely OOMKilled failure"
                ),
                "type": "agent"
            },

            {
                "timestamp": "2026-09-10T10:35:00",
                "event": (
                    "Remediation Agent generated "
                    "a safe remediation plan"
                ),
                "type": "agent"
            },

            {
                "timestamp": "2026-09-10T10:36:00",
                "event": (
                    "Safety Gate protected destructive "
                    "actions with human approval"
                ),
                "type": "safety"
            },

            {
                "timestamp": "2026-09-10T10:37:00",
                "event": (
                    "Blameless RCA generated "
                    "for INC-001"
                ),
                "type": "rca"
            }

        ]

    }


# ============================================================
# RCA
# ============================================================

@app.get("/rca")
def get_rca():

    rca_path = os.path.join(
        PROJECT_ROOT,
        "rca",
        "incident_rca.json"
    )


    if not os.path.exists(rca_path):

        return {
            "error": "RCA has not been generated yet."
        }


    with open(
        rca_path,
        "r",
        encoding="utf-8"
    ) as file:

        rca = json.load(file)


    return rca


# ============================================================
# HUMAN APPROVAL
# ============================================================

class ApprovalRequest(BaseModel):

    action: str

    approved: bool


@app.post("/approve")
def approve_action(request: ApprovalRequest):

    # --------------------------------------------------------
    # Normalize action
    # --------------------------------------------------------

    action = request.action.strip()

    action_lower = action.lower()


    # --------------------------------------------------------
    # Destructive keywords
    # --------------------------------------------------------

    destructive_keywords = [

        "delete",

        "drop",

        "reboot",

        "rollback",

        "roll back",

        "terminate",

        "shutdown"

    ]


    is_destructive = any(

        keyword in action_lower

        for keyword in destructive_keywords

    )


    # ========================================================
    # DESTRUCTIVE ACTION
    # ========================================================

    if is_destructive:

        # ----------------------------------------------------
        # APPROVED
        # ----------------------------------------------------

        if request.approved:

            approval_state[action] = {

                "approval_status": "APPROVED",

                "human_approval": "GRANTED",

                "execution": "SIMULATED"

            }


            incident_state["status"] = (
                "REMEDIATION APPROVED"
            )


            return {

                "action": action,

                "safety_status": "APPROVED",

                "human_approval": "GRANTED",

                "approval_status": "APPROVED",

                "execution": "SIMULATED",

                "message": (
                    "Human approval granted. "
                    "Execution remains simulated "
                    "in this MVP."
                )

            }


        # ----------------------------------------------------
        # DENIED
        # ----------------------------------------------------

        else:

            approval_state[action] = {

                "approval_status": "DENIED",

                "human_approval": "DENIED",

                "execution": "BLOCKED"

            }


            return {

                "action": action,

                "safety_status": "BLOCKED",

                "human_approval": "DENIED",

                "approval_status": "DENIED",

                "execution": "BLOCKED",

                "message": (
                    "Human approval denied. "
                    "The destructive action was not executed."
                )

            }


    # ========================================================
    # NON-DESTRUCTIVE ACTION
    # ========================================================

    approval_state[action] = {

        "approval_status": "APPROVED",

        "human_approval": "NOT REQUIRED",

        "execution": "SIMULATED"

    }


    return {

        "action": action,

        "safety_status": "APPROVED",

        "human_approval": "NOT REQUIRED",

        "approval_status": "APPROVED",

        "execution": "SIMULATED",

        "message": (
            "Non-destructive action is safe "
            "for the current MVP."
        )

    }