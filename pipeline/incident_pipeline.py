import sys
import os

# Allow imports from the project root
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from agents.triage_agent import triage_incident, load_alerts
from agents.diagnostic_agent import diagnose_incident, load_json
from agents.remediation_agent import create_remediation_plan
from safety.remediation_gate import process_action
from rca.rca_generator import generate_rca, save_rca


def run_incident_pipeline():

    print("\n")
    print("========================================")
    print("      SRE INCIDENT RESPONSE PIPELINE")
    print("========================================")

    # --------------------------------------
    # 1. Alert Ingestion
    # --------------------------------------

    alerts = load_alerts()
    logs = load_json("logs.json")
    deployments = load_json("deployments.json")

    print("\n[1] ALERT INGESTION")
    print(f"Received {len(alerts)} alerts.")

    # --------------------------------------
    # 2. Triage
    # --------------------------------------

    print("\n[2] TRIAGE")

    triage_result = triage_incident(alerts)

    print(f"Incident: {triage_result['incident']}")
    print(f"Service: {triage_result['affected_service']}")
    print(f"Severity: {triage_result['severity']}")

    # --------------------------------------
    # 3. Root Cause Diagnosis
    # --------------------------------------

    print("\n[3] ROOT CAUSE DIAGNOSIS")

    diagnosis_result = diagnose_incident(
        alerts,
        logs,
        deployments
    )

    print(f"Confidence: {diagnosis_result['confidence']}")

    print("\nRoot Cause:")
    print(diagnosis_result["root_cause"])

    # --------------------------------------
    # 4. Remediation Proposal
    # --------------------------------------

    print("\n[4] REMEDIATION PROPOSAL")

    remediation_result = create_remediation_plan(
        alerts,
        logs,
        deployments
    )

    for action in remediation_result["recommended_actions"]:

        print(
            f"- {action['action']} "
            f"[Risk: {action['risk']}]"
        )

    # --------------------------------------
    # 5. Safety Gate / HITL
    # --------------------------------------

    print("\n[5] SAFETY GATE")

    remediation_decisions = []

    for action in remediation_result["recommended_actions"]:

        decision = process_action(
            action["action"]
        )

        remediation_decisions.append({
            "action": action["action"],
            "risk": action["risk"],
            "decision": decision
        })

    # --------------------------------------
    # 6. Generate RCA
    # --------------------------------------

    print("\n[6] BLAMELESS RCA")

    rca = generate_rca(
        alerts,
        logs,
        deployments
    )

    # Add actual safety decisions to RCA
    rca["remediation_decisions"] = remediation_decisions

    save_rca(rca)

    print("\nRCA generated successfully.")
    print("Saved to:")
    print("rca/incident_rca.json")

    # --------------------------------------
    # Complete
    # --------------------------------------

    print("\n========================================")
    print("       INCIDENT PIPELINE COMPLETE")
    print("========================================")


if __name__ == "__main__":
    run_incident_pipeline()