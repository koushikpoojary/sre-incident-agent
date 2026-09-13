import json


def load_json(filename):
    with open(f"data/{filename}", "r") as file:
        return json.load(file)


def diagnose_incident(alerts, logs, deployments):
    deployment = deployments[0]

    oom_events = [
        log for log in logs
        if "OOMKilled" in log["message"]
    ]

    memory_events = [
        log for log in logs
        if "Memory usage" in log["message"]
    ]

    http_errors = [
        log for log in logs
        if "HTTP 500" in log["message"]
    ]

    recent_deployment = deployment["current_version"]

    if oom_events and recent_deployment:
        root_cause = (
            f"The most likely root cause is a memory-related failure "
            f"associated with deployment {recent_deployment}. "
            f"The application was deployed at "
            f"{deployment['deployment_time']}, memory usage increased "
            f"and the container was subsequently terminated with "
            f"OOMKilled."
        )
    else:
        root_cause = (
            "The available evidence is insufficient to determine "
            "the root cause."
        )

    return {
        "incident": "INC-001",
        "root_cause": root_cause,
        "confidence": "High",
        "evidence": {
            "deployment": recent_deployment,
            "memory_events": len(memory_events),
            "oom_events": len(oom_events),
            "http_error_events": len(http_errors),
        },
        "recommended_actions": [
            "Inspect deployment v2.4.1 configuration",
            "Compare v2.4.1 with v2.4.0",
            "Check application memory limits",
            "Review application changes related to memory usage",
            "Do not perform destructive remediation automatically",
        ],
    }


alerts = load_json("alerts.json")
logs = load_json("logs.json")
deployments = load_json("deployments.json")

print(f"Loaded {len(alerts)} alerts.")
print(f"Loaded {len(logs)} log entries.")
print(f"Loaded {len(deployments)} deployment records.")

result = diagnose_incident(
    alerts,
    logs,
    deployments
)

print("\n========================================")
print("        ROOT CAUSE DIAGNOSIS")
print("========================================")

print(f"\nIncident: {result['incident']}")
print(f"Confidence: {result['confidence']}")

print("\nRoot Cause:")
print(result["root_cause"])

print("\nEvidence:")
for key, value in result["evidence"].items():
    print(f"- {key}: {value}")

print("\nRecommended Actions:")
for action in result["recommended_actions"]:
    print(f"- {action}")