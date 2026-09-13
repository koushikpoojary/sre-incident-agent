import json


def load_json(filename):
    with open(f"data/{filename}", "r") as file:
        return json.load(file)


def create_remediation_plan(alerts, logs, deployments):
    deployment = deployments[0]

    # Look for evidence from the diagnostic data
    has_oom = any(
        "OOMKilled" in log["message"]
        for log in logs
    )

    has_high_memory = any(
        "Memory usage" in log["message"]
        for log in logs
    )

    has_http_errors = any(
        "HTTP 500" in log["message"]
        for log in logs
    )

    actions = []

    # Safe investigation actions
    actions.append({
        "action": "Inspect deployment v2.4.1 configuration",
        "risk": "LOW",
        "requires_human_approval": False
    })

    actions.append({
        "action": "Compare v2.4.1 with v2.4.0",
        "risk": "LOW",
        "requires_human_approval": False
    })

    actions.append({
        "action": "Check payment-api memory limits",
        "risk": "LOW",
        "requires_human_approval": False
    })

    # Destructive/high-risk actions require HITL
    if has_oom and has_high_memory:

        actions.append({
            "action": "Roll back deployment v2.4.1 to v2.4.0",
            "risk": "HIGH",
            "requires_human_approval": True
        })

        actions.append({
            "action": "kubectl delete pod payment-api",
            "risk": "HIGH",
            "requires_human_approval": True
        })

    if has_http_errors:

        actions.append({
            "action": "Investigate HTTP 500 errors in payment-api logs",
            "risk": "LOW",
            "requires_human_approval": False
        })

    return {
        "incident": "INC-001",
        "service": deployment["service"],
        "current_version": deployment["current_version"],
        "recommended_actions": actions
    }


# --------------------------------------------------
# Standalone test
# --------------------------------------------------

if __name__ == "__main__":

    alerts = load_json("alerts.json")
    logs = load_json("logs.json")
    deployments = load_json("deployments.json")

    result = create_remediation_plan(
        alerts,
        logs,
        deployments
    )

    print("========================================")
    print("        REMEDIATION PLAN")
    print("========================================")

    print(f"\nIncident: {result['incident']}")
    print(f"Service: {result['service']}")
    print(f"Current Version: {result['current_version']}")

    print("\nProposed Actions:")

    for index, action in enumerate(
        result["recommended_actions"],
        start=1
    ):

        print(f"\n{index}. {action['action']}")
        print(f"   Risk: {action['risk']}")

        if action["requires_human_approval"]:
            print("   HITL: REQUIRED")
        else:
            print("   HITL: NOT REQUIRED")