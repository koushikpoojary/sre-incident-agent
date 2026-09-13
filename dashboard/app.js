const API_URL = "http://127.0.0.1:8000";


// ============================================================
// GLOBAL APPROVAL STATE
// ============================================================

let approvalStates = {};


// ============================================================
// LOAD INCIDENT
// ============================================================

async function loadIncident() {

    try {

        const incidentResponse = await fetch(
            `${API_URL}/incident`
        );

        if (!incidentResponse.ok) {
            throw new Error("Incident API request failed");
        }

        const data = await incidentResponse.json();


        // Load alerts

        const alertsResponse = await fetch(
            `${API_URL}/alerts`
        );

        if (!alertsResponse.ok) {
            throw new Error("Alerts API request failed");
        }

        const alertsData = await alertsResponse.json();


        displayIncident(
            data,
            alertsData.alerts || []
        );


        // Load RCA

        await loadRCA();


        // Load Timeline

        await loadTimeline();


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );


        const rootCause =
            document.getElementById("root-cause");


        if (rootCause) {

            rootCause.textContent =
                "Unable to connect to the SRE API.";

        }

    }

}


// ============================================================
// DISPLAY INCIDENT
// ============================================================

function displayIncident(data, allAlerts) {

    const incident = data.incident || {};

    const diagnosis = data.diagnosis || {};

    const remediation = data.remediation || {};


    // --------------------------------------------------------
    // Incident Overview
    // --------------------------------------------------------

    const incidentId =
        document.getElementById("incident-id");


    if (incidentId) {

        incidentId.textContent =
            incident.incident || "Unknown";

    }


    const service =
        document.getElementById("service");


    if (service) {

        service.textContent =
            incident.affected_service || "Unknown";

    }


    const severityText =
        document.getElementById("severity-text");


    if (severityText) {

        severityText.textContent =
            incident.severity || "Unknown";

    }


    const severity =
        document.getElementById("severity");


    if (severity) {

        severity.textContent =
            incident.severity || "Unknown";

    }


    // --------------------------------------------------------
    // Incident Status
    // --------------------------------------------------------

    const statusElement =
        document.getElementById("incident-status");


    if (statusElement) {

        statusElement.textContent =
            data.status || "INVESTIGATING";

    }


    // --------------------------------------------------------
    // Root Cause Confidence
    // --------------------------------------------------------

    const confidence =
        document.getElementById("confidence");


    if (confidence) {

        confidence.textContent =
            diagnosis.confidence || "Unknown";

    }


    // --------------------------------------------------------
    // Root Cause
    // --------------------------------------------------------

    const rootCause =
        document.getElementById("root-cause");


    if (rootCause) {

        rootCause.textContent =
            diagnosis.root_cause ||
            "Root cause not available.";

    }


    // ========================================================
    // ALERTS
    // ========================================================

    const alertsContainer =
        document.getElementById("alerts-container");


    const alertCount =
        document.getElementById("alert-count");


    const relatedAlertIds =
        incident.related_alerts || [];


    const alerts =
        allAlerts.filter(
            alert =>
                relatedAlertIds.includes(
                    alert.alert_id
                )
        );


    if (alertCount) {

        alertCount.textContent =
            `${alerts.length} alerts`;

    }


    if (alertsContainer) {

        alertsContainer.innerHTML = "";


        if (alerts.length === 0) {

            alertsContainer.innerHTML =
                "<p>No correlated alerts found.</p>";

        }


        alerts.forEach(alert => {

            const alertElement =
                document.createElement("div");


            alertElement.className =
                "alert";


            alertElement.innerHTML = `

                <div class="alert-info">

                    <strong>
                        ${escapeHtml(alert.alert_type)}
                    </strong>

                    <span class="alert-message">
                        ${escapeHtml(alert.message)}
                    </span>

                </div>

                <div class="alert-severity">
                    ${escapeHtml(alert.severity)}
                </div>

            `;


            alertsContainer.appendChild(
                alertElement
            );

        });

    }


    // ========================================================
    // REMEDIATION
    // ========================================================

    displayRemediation(
        remediation.recommended_actions || []
    );

}


// ============================================================
// DISPLAY REMEDIATION
// ============================================================

function displayRemediation(actions) {

    const remediationContainer =
        document.getElementById(
            "remediation-container"
        );


    if (!remediationContainer) {
        return;
    }


    remediationContainer.innerHTML = "";


    if (!actions.length) {

        remediationContainer.innerHTML =
            "<p>No remediation actions available.</p>";

        return;

    }


    actions.forEach((action, index) => {

        const element =
            document.createElement("div");


        element.className =
            "remediation";


        // ----------------------------------------------------
        // Risk
        // ----------------------------------------------------

        const riskClass =
            action.risk === "HIGH"
                ? "risk-high"
                : "risk-low";


        // ----------------------------------------------------
        // Current approval state
        // ----------------------------------------------------

        let approval;


        /*
         * IMPORTANT:
         *
         * The backend now returns:
         *
         * approval_status
         * human_approval
         * execution
         *
         * Therefore we use those values instead of checking
         * only whether risk is HIGH.
         */


        if (
            action.approval_status === "APPROVED" &&
            action.human_approval === "GRANTED"
        ) {

            approval = `

                <div class="approval-result">

                    <span class="approved approval-granted">
                        ✓ APPROVED
                    </span>

                    <small>
                        Human approval granted
                    </small>

                    <small>
                        Execution: ${escapeHtml(
                            action.execution || "SIMULATED"
                        )}
                    </small>

                </div>

            `;

        }


        else if (
            action.approval_status === "BLOCKED" ||
            action.human_approval === "DENIED"
        ) {

            approval = `

                <div class="approval-result">

                    <span class="approved approval-denied">
                        BLOCKED
                    </span>

                    <small>
                        Human approval denied
                    </small>

                </div>

            `;

        }


        else if (
            action.risk === "HIGH" &&
            action.requires_human_approval === true
        ) {

            approval = `

                <button
                    class="approve-button"
                    id="approve-button-${index}"
                    data-action-index="${index}">
                    Review & Approve
                </button>

            `;

        }


        else {

            approval = `

                <span class="approved">
                    ✓ APPROVED
                </span>

            `;

        }


        // ----------------------------------------------------
        // Remediation card
        // ----------------------------------------------------

        element.innerHTML = `

            <div>

                <strong>
                    ${escapeHtml(action.action)}
                </strong>

                <div class="${riskClass}">
                    Risk: ${escapeHtml(action.risk)}
                </div>

            </div>


            <div id="approval-container-${index}">
                ${approval}
            </div>

        `;


        remediationContainer.appendChild(
            element
        );


        // ----------------------------------------------------
        // Add click listener
        // ----------------------------------------------------

        if (
            action.risk === "HIGH" &&
            action.requires_human_approval === true &&
            action.approval_status !== "APPROVED" &&
            action.approval_status !== "BLOCKED"
        ) {

            const button =
                document.getElementById(
                    `approve-button-${index}`
                );


            if (button) {

                button.addEventListener(
                    "click",
                    function () {

                        requestApproval(
                            action.action,
                            button,
                            index
                        );

                    }
                );

            }

        }

    });

}


// ============================================================
// HUMAN APPROVAL
// ============================================================

async function requestApproval(
    action,
    button,
    index
) {

    const approved = confirm(

        "This action may be destructive:\n\n" +

        action +

        "\n\n" +

        "Do you want to approve this action?"

    );


    // --------------------------------------------------------
    // User denied approval
    // --------------------------------------------------------

    if (!approved) {

        button.textContent =
            "Approval Denied";


        button.classList.add(
            "approval-denied"
        );


        button.disabled = true;


        return;

    }


    // --------------------------------------------------------
    // Processing
    // --------------------------------------------------------

    button.textContent =
        "Processing...";


    button.disabled = true;


    try {

        const response = await fetch(

            `${API_URL}/approve`,

            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body: JSON.stringify({

                    action: action,

                    approved: true

                })

            }

        );


        if (!response.ok) {

            throw new Error(
                "Approval API request failed"
            );

        }


        const result =
            await response.json();


        console.log(
            "Approval response:",
            result
        );


        // ====================================================
        // APPROVED
        // ====================================================

        if (

            result.approval_status === "APPROVED" ||

            (
                result.human_approval === "GRANTED" &&
                result.safety_status === "APPROVED"
            )

        ) {

            /*
             * Save approval locally so the UI remains correct
             * even before the next API refresh.
             */

            approvalStates[action] = {

                approval_status: "APPROVED",

                human_approval: "GRANTED",

                execution:
                    result.execution || "SIMULATED"

            };


            // Change button

            button.textContent =
                "✓ APPROVED";


            button.classList.remove(
                "approval-denied"
            );


            button.classList.add(
                "approval-granted"
            );


            button.disabled = true;


            // Replace button with permanent approval state

            const container =
                document.getElementById(
                    `approval-container-${index}`
                );


            if (container) {

                container.innerHTML = `

                    <div class="approval-result">

                        <span class="approved approval-granted">
                            ✓ APPROVED
                        </span>

                        <small>
                            Human approval granted
                        </small>

                        <small>
                            Execution: ${escapeHtml(
                                result.execution || "SIMULATED"
                            )}
                        </small>

                    </div>

                `;

            }


            alert(

                "HUMAN APPROVAL GRANTED\n\n" +

                result.message

            );


            /*
             * Refresh incident data from backend.
             *
             * This ensures the dashboard gets the persisted
             * approval_status from /incident.
             */

            await refreshIncidentAfterApproval();

        }


        // ====================================================
        // BLOCKED
        // ====================================================

        else {

            button.textContent =
                "BLOCKED";


            button.classList.add(
                "approval-denied"
            );


            button.disabled = true;


            alert(

                "ACTION BLOCKED\n\n" +

                (
                    result.message ||
                    "Action was blocked."
                )

            );

        }


    } catch (error) {

        console.error(
            "Approval error:",
            error
        );


        button.textContent =
            "Review & Approve";


        button.disabled = false;


        alert(
            "Could not contact the safety gate."
        );

    }

}


// ============================================================
// REFRESH AFTER APPROVAL
// ============================================================

async function refreshIncidentAfterApproval() {

    try {

        const incidentResponse =
            await fetch(
                `${API_URL}/incident`
            );


        if (!incidentResponse.ok) {
            return;
        }


        const data =
            await incidentResponse.json();


        const alertsResponse =
            await fetch(
                `${API_URL}/alerts`
            );


        if (!alertsResponse.ok) {
            return;
        }


        const alertsData =
            await alertsResponse.json();


        /*
         * Re-render the incident.
         *
         * Since the backend now returns approval_status,
         * the approved action will remain APPROVED.
         */

        displayIncident(
            data,
            alertsData.alerts || []
        );


        // Keep RCA and timeline updated

        await loadRCA();

        await loadTimeline();


    } catch (error) {

        console.error(
            "Refresh after approval error:",
            error
        );

    }

}


// ============================================================
// LOAD RCA
// ============================================================

async function loadRCA() {

    try {

        const response =
            await fetch(
                `${API_URL}/rca`
            );


        if (!response.ok) {

            throw new Error(
                "RCA API request failed"
            );

        }


        const rca =
            await response.json();


        displayRCA(rca);


    } catch (error) {

        console.error(
            "RCA error:",
            error
        );

    }

}


// ============================================================
// DISPLAY RCA
// ============================================================

function displayRCA(rca) {

    const container =
        document.getElementById(
            "rca-container"
        );


    if (!container) {
        return;
    }


    if (rca.error) {

        container.textContent =
            "RCA has not been generated yet.";

        return;

    }


    let html = "";


    // --------------------------------------------------------
    // Summary
    // --------------------------------------------------------

    html += `

        <h3>
            Incident Summary
        </h3>

        <p>
            ${escapeHtml(rca.summary)}
        </p>

    `;


    // --------------------------------------------------------
    // Impact
    // --------------------------------------------------------

    html += `

        <h3>
            Impact
        </h3>

        <p>
            ${escapeHtml(rca.impact)}
        </p>

    `;


    // --------------------------------------------------------
    // Timeline
    // --------------------------------------------------------

    html += `

        <h3>
            Timeline
        </h3>

    `;


    if (rca.timeline) {

        rca.timeline.forEach(
            event => {

                html += `

                    <div class="timeline-item">

                        <div class="timeline-time">
                            ${escapeHtml(
                                event.timestamp
                            )}
                        </div>

                        <div>
                            ${escapeHtml(
                                event.event
                            )}
                        </div>

                    </div>

                `;

            }
        );

    }


    // --------------------------------------------------------
    // Root Cause
    // --------------------------------------------------------

    html += `

        <h3>
            Root Cause
        </h3>

        <p>
            ${escapeHtml(rca.root_cause)}
        </p>

    `;


    // --------------------------------------------------------
    // Prevention
    // --------------------------------------------------------

    html += `

        <h3>
            Prevention
        </h3>

        <ul>

    `;


    if (rca.prevention) {

        rca.prevention.forEach(
            item => {

                html += `

                    <li>
                        ${escapeHtml(item)}
                    </li>

                `;

            }
        );

    }


    html += `

        </ul>

    `;


    container.innerHTML =
        html;

}


// ============================================================
// LOAD INCIDENT TIMELINE
// ============================================================

async function loadTimeline() {

    try {

        const response =
            await fetch(
                `${API_URL}/timeline`
            );


        if (!response.ok) {

            throw new Error(
                "Timeline API request failed"
            );

        }


        const data =
            await response.json();


        displayTimeline(
            data.timeline || []
        );


    } catch (error) {

        console.error(
            "Timeline error:",
            error
        );

    }

}


// ============================================================
// DISPLAY TIMELINE
// ============================================================

function displayTimeline(timeline) {

    const container =
        document.getElementById(
            "timeline-container"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (!timeline.length) {

        container.innerHTML = `

            <p>
                No incident events available.
            </p>

        `;

        return;

    }


    timeline.forEach(item => {

        const element =
            document.createElement(
                "div"
            );


        element.className =
            "timeline-event";


        let severityBadge = "";


        if (item.severity) {

            severityBadge = `

                <span class="timeline-severity">
                    ${escapeHtml(
                        item.severity
                    )}
                </span>

            `;

        }


        element.innerHTML = `

            <div class="timeline-time">
                ${escapeHtml(
                    item.timestamp || "Unknown time"
                )}
            </div>

            <div class="timeline-marker">
                ●
            </div>

            <div class="timeline-description">

                ${escapeHtml(
                    item.event
                )}

                ${severityBadge}

            </div>

        `;


        container.appendChild(
            element
        );

    });

}


// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// ============================================================
// START DASHBOARD
// ============================================================

loadIncident();