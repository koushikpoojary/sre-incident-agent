import json


def load_json(filename):
    with open(f"data/{filename}", "r") as file:
        return json.load(file)


def generate_rca(alerts, logs, deployments):

    deployment = deployments[0]

    # Sort alerts by timestamp
    sorted_alerts = sorted(
        alerts,
        key=lambda x: x["timestamp"]
    )

    # Build incident timeline
    timeline = []

    timeline.append({
        "timestamp": deployment["deployment_time"],
        "event": (
            f"Deployment {deployment['current_version']} "
            f"released to {deployment['service']}"
        )
    })

    for alert in sorted_alerts:
        timeline.append({
            "timestamp": alert["timestamp"],
            "event": alert["message"]
        })

    timeline.sort(key=lambda x: x["timestamp"])

    rca = {
        "incident_id": "INC-001",
        "severity": "P1",
        "service": deployment["service"],

        "summary": (
            "The payment-api service experienced a P1 incident "
            "involving high memory usage, pod instability, "
            "and elevated HTTP 500 errors."
        ),

        "impact": (
            "HTTP 500 error rates increased to approximately 35%, "
            "and the payment-api pod experienced a restart."
        ),

        "timeline": timeline,

        "root_cause": (
            f"The most likely root cause was a memory-related failure "
            f"associated with deployment "
            f"{deployment['current_version']}. "
            "Memory usage increased after the deployment and the "
            "container was subsequently terminated with OOMKilled."
        ),

        "contributing_factors": [
            "High application memory consumption",
            "Pod instability following the memory increase",
            "Production deployment preceded the observed failure",
            "Insufficient early detection of the memory regression"
        ],

        "remediation": [
            "Inspect deployment v2.4.1 configuration",
            "Compare v2.4.1 with v2.4.0",
            "Review payment-api memory limits",
            "Investigate application memory behavior",
            "Require human approval for rollback or pod deletion"
        ],

        "prevention": [
            "Add memory regression testing before production deployment",
            "Review Kubernetes resource requests and limits",
            "Improve memory monitoring and alerting",
            "Add deployment health checks",
            "Document rollback procedures"
        ],

        "blameless_note": (
            "The incident resulted from application memory behavior "
            "combined with the production deployment. The response "
            "process identified correlated alerts and established "
            "a likely failure path. No individual or team is assigned "
            "blame for the incident."
        )
    }

    return rca


def save_rca(rca):

    with open("rca/incident_rca.json", "w") as file:
        json.dump(rca, file, indent=2)


def print_rca(rca):

    print("\n========================================")
    print("          BLAMELESS INCIDENT RCA")
    print("========================================")

    print(f"\nIncident: {rca['incident_id']}")
    print(f"Severity: {rca['severity']}")
    print(f"Service: {rca['service']}")

    print("\nSummary:")
    print(rca["summary"])

    print("\nImpact:")
    print(rca["impact"])

    print("\nTimeline:")

    for event in rca["timeline"]:
        print(
            f"- {event['timestamp']} : "
            f"{event['event']}"
        )

    print("\nRoot Cause:")
    print(rca["root_cause"])

    print("\nContributing Factors:")

    for item in rca["contributing_factors"]:
        print(f"- {item}")

    print("\nRemediation:")

    for item in rca["remediation"]:
        print(f"- {item}")

    print("\nPrevention:")

    for item in rca["prevention"]:
        print(f"- {item}")

    print("\nBlameless Note:")
    print(rca["blameless_note"])

    print("\nRCA saved to:")
    print("rca/incident_rca.json")


if __name__ == "__main__":

    alerts = load_json("alerts.json")
    logs = load_json("logs.json")
    deployments = load_json("deployments.json")

    rca = generate_rca(
        alerts,
        logs,
        deployments
    )

    save_rca(rca)
    print_rca(rca)