DESTRUCTIVE_ACTIONS = [
    "DELETE",
    "DROP",
    "REBOOT",
    "TERMINATE",
    "DESTROY",
    "ROLL BACK",
    "ROLLBACK",
    "SCALE DOWN",
    "DEPLOY",
    "UPDATE"
]


def is_destructive(action):
    """
    Check whether an action contains a destructive
    operation as a complete word/phrase.
    """

    action_upper = action.upper()

    words = action_upper.replace(",", " ").split()

    for destructive_action in DESTRUCTIVE_ACTIONS:

        # Handle multi-word actions such as ROLL BACK
        if " " in destructive_action:
            if destructive_action in action_upper:
                return True

        # Handle single-word actions
        elif destructive_action in words:
            return True

    return False


def safety_check(action):

    if is_destructive(action):
        return {
            "status": "BLOCKED",
            "reason": "Destructive action requires human approval.",
            "requires_human_approval": True
        }

    return {
        "status": "APPROVED",
        "reason": "Action is classified as non-destructive.",
        "requires_human_approval": False
    }


def request_human_approval(action):

    print("\n========================================")
    print("       HUMAN APPROVAL REQUIRED")
    print("========================================")

    print("\nProposed Action:")
    print(action)

    print("\nThis action is potentially destructive.")
    print("It will NOT be executed without approval.")

    while True:

        choice = input(
            "\nApprove this action? (yes/no): "
        ).strip().lower()

        if choice in ["yes", "y"]:
            return True

        if choice in ["no", "n"]:
            return False

        print("Please enter yes or no.")


def process_action(action):

    result = safety_check(action)

    print(f"\nAction: {action}")
    print(f"Safety Status: {result['status']}")
    print(f"Reason: {result['reason']}")

    if result["requires_human_approval"]:

        approved = request_human_approval(action)

        if approved:
            print("\nHuman Approval: GRANTED")
            print("Execution: SIMULATED")

            return "APPROVED_BY_HUMAN"

        print("\nHuman Approval: DENIED")
        print("Execution: BLOCKED")

        return "DENIED"

    print("Human Approval: NOT REQUIRED")
    print("Execution: SIMULATED")

    return "APPROVED"


if __name__ == "__main__":

    test_actions = [
        "Inspect deployment v2.4.1 configuration",
        "Compare v2.4.1 with v2.4.0",
        "Check payment-api memory limits",
        "Roll back deployment v2.4.1 to v2.4.0",
        "kubectl delete pod payment-api-123"
    ]

    print("========================================")
    print("       REMEDIATION SAFETY GATE")
    print("========================================")

    for action in test_actions:
        process_action(action)