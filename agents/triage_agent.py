import json


def load_alerts():
    with open("data/alerts.json", "r") as file:
        return json.load(file)


def triage_incident(alerts):
    services = set(alert["service"] for alert in alerts)

    p1_alerts = [
        alert for alert in alerts
        if alert["severity"] == "P1"
    ]

    alert_types = [alert["alert_type"] for alert in alerts]

    # Simple correlation logic for our MVP
    if len(services) == 1:
        affected_service = list(services)[0]
    else:
        affected_service = "Multiple services"

    if p1_alerts:
        severity = "P1"
    elif any(alert["severity"] == "P2" for alert in alerts):
        severity = "P2"
    elif any(alert["severity"] == "P3" for alert in alerts):
        severity = "P3"
    else:
        severity = "P4"

    related = (
        "HighMemoryUsage" in alert_types
        and "PodRestarting" in alert_types
        and "HTTP5xx" in alert_types
    )

    if related:
        assessment = (
            "The alerts are likely related to the same incident. "
            "The payment-api service is experiencing high memory usage, "
            "pod instability, and elevated HTTP 500 errors."
        )
    else:
        assessment = (
            "The alerts require further investigation to determine "
            "whether they belong to the same incident."
        )

    return {
        "incident": "INC-001",
        "affected_service": affected_service,
        "severity": severity,
        "related_alerts": [alert["alert_id"] for alert in alerts],
        "alert_types": alert_types,
        "assessment": assessment,
        "next_investigation": [
            "Check Kubernetes pod status",
            "Inspect application logs",
            "Check recent deployments",
            "Investigate memory consumption",
        ],
    }


alerts = load_alerts()

print(f"Loaded {len(alerts)} alerts.")

result = triage_incident(alerts)

print("\n========================================")
print("          INCIDENT TRIAGE RESULT")
print("========================================")

print(f"\nIncident: {result['incident']}")
print(f"Affected Service: {result['affected_service']}")
print(f"Severity: {result['severity']}")

print("\nRelated Alerts:")
for alert_id in result["related_alerts"]:
    print(f"- {alert_id}")

print("\nAlert Types:")
for alert_type in result["alert_types"]:
    print(f"- {alert_type}")

print("\nAssessment:")
print(result["assessment"])

print("\nNext Investigation:")
for step in result["next_investigation"]:
    print(f"- {step}")