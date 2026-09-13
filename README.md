\# SRE Incident Agent



A governed multi-agent SRE incident response system for automated incident triage, root cause diagnosis, remediation planning, human approval, and blameless Root Cause Analysis (RCA).



\## Overview



The SRE Incident Agent is a prototype incident response system designed to demonstrate how multiple specialized agents can work together to investigate and respond to production-style incidents.



The system takes incident alerts and operational data as input and processes them through a sequence of specialized agents.



The main workflow is:



1\. Alert ingestion

2\. Incident triage

3\. Root cause diagnosis

4\. Remediation planning

5\. Safety evaluation

6\. Human approval for high-risk actions

7\. Simulated remediation execution

8\. Blameless RCA generation



The system is designed with safety and Human-in-the-Loop (HITL) controls so that potentially destructive actions are not executed automatically.



\## Key Features



\- Multi-agent incident investigation

\- Alert correlation

\- Incident severity identification

\- Root cause analysis

\- Evidence-based diagnosis

\- Risk-based remediation planning

\- Human-in-the-Loop approval

\- Safety gate for destructive actions

\- Simulated remediation execution

\- Incident timeline

\- Blameless RCA generation

\- FastAPI backend

\- Web-based incident dashboard



\## Architecture



```text

&#x20;                        Incident Alerts

&#x20;                              |

&#x20;                              v

&#x20;                   +---------------------+

&#x20;                   |   Alert Ingestion   |

&#x20;                   +----------+----------+

&#x20;                              |

&#x20;                              v

&#x20;                   +---------------------+

&#x20;                   |    Triage Agent     |

&#x20;                   +----------+----------+

&#x20;                              |

&#x20;                              v

&#x20;                   +---------------------+

&#x20;                   | Diagnostic Agent    |

&#x20;                   +----------+----------+

&#x20;                              |

&#x20;                              v

&#x20;                   +---------------------+

&#x20;                   | Remediation Agent   |

&#x20;                   +----------+----------+

&#x20;                              |

&#x20;                              v

&#x20;                   +---------------------+

&#x20;                   |     Safety Gate     |

&#x20;                   +----------+----------+

&#x20;                              |

&#x20;                   +----------+----------+

&#x20;                   |                     |

&#x20;                   v                     v

&#x20;            Low-Risk Action       High-Risk Action

&#x20;                   |                     |

&#x20;                   v                     v

&#x20;             Auto Approved        Human Approval

&#x20;                   |                     |

&#x20;                   |              +------+------+

&#x20;                   |              |             |

&#x20;                   |              v             v

&#x20;                   |          Approved        Denied

&#x20;                   |              |             |

&#x20;                   |              v             v

&#x20;                   |          Simulated      Blocked

&#x20;                   |          Execution

&#x20;                   |              |

&#x20;                   +--------------+

&#x20;                              |

&#x20;                              v

&#x20;                   +---------------------+

&#x20;                   |   Blameless RCA     |

&#x20;                   +---------------------+

&#x20;                              |

&#x20;                              v

&#x20;                        SRE Dashboard

**Project Structure**

sre-incident-agent/

│

├── agents/

│   ├── triage\_agent.py

│   ├── diagnostic\_agent.py

│   └── remediation\_agent.py

│

├── api/

│   └── main.py

│

├── dashboard/

│   ├── index.html

│   ├── app.js

│   └── style.css

│

├── data/

│   ├── alerts.json

│   ├── deployments.json

│   ├── logs.json

│   └── test\_data.py

│

├── pipeline/

│   └── incident\_pipeline.py

│

├── rca/

│   ├── rca\_generator.py

│   └── incident\_rca.json

│

├── safety/

│   └── remediation\_gate.py

│

├── requirements.txt

├── test\_data.py

├── .gitignore

└── README.md


**Agent Workflow**





**1. Alert Ingestion**



The system loads incident alerts from the data layer.



The sample incident contains three related alerts:



ALT-001 - HighMemoryUsage

ALT-002 - PodRestarting

ALT-003 - HTTP5xx



These alerts represent different symptoms of the same service incident.



**2. Triage Agent**



The Triage Agent analyzes the incoming alerts and determines whether they are related to the same incident.



For the sample incident:



Incident: INC-001

Affected Service: payment-api

Severity: P1



The agent correlates the alerts and creates an incident assessment.



**3. Diagnostic Agent**



The Diagnostic Agent analyzes available operational evidence such as:



Alerts

Application logs

Deployment information

Memory events

OOM events

HTTP errors



For the sample incident, the diagnostic result is:



Incident: INC-001

Confidence: High

Deployment: v2.4.1

Memory Events: 2

OOM Events: 1

HTTP Error Events: 1



The most likely root cause is a memory-related failure associated with deployment v2.4.1.



**4. Remediation Agent**



The Remediation Agent generates recommended actions based on the diagnosis.



Example remediation actions:



Inspect deployment v2.4.1 configuration

Risk: LOW



Compare v2.4.1 with v2.4.0

Risk: LOW



Check payment-api memory limits

Risk: LOW



Roll back deployment v2.4.1 to v2.4.0

Risk: HIGH



kubectl delete pod payment-api

Risk: HIGH



Investigate HTTP 500 errors in payment-api logs

Risk: LOW



Each action is classified based on its potential risk.


**5. Safety Gate**



The Safety Gate protects potentially destructive actions.



Low-risk actions can be approved automatically.



High-risk actions require explicit human approval.



Example:



Action:

Roll back deployment v2.4.1 to v2.4.0



Risk:

HIGH



Human Approval:

REQUIRED



**6. Human-in-the-Loop Approval**



The API provides an approval endpoint for high-risk actions.



Example request:



{

&#x20; "action": "Roll back deployment v2.4.1 to v2.4.0",

&#x20; "approved": true

}



Example approved response:



{

&#x20; "action": "Roll back deployment v2.4.1 to v2.4.0",

&#x20; "safety\_status": "APPROVED",

&#x20; "human\_approval": "GRANTED",

&#x20; "approval\_status": "APPROVED",

&#x20; "execution": "SIMULATED",

&#x20; "message": "Human approval granted. Execution remains simulated in this MVP."

}



If the user denies the action, the action is blocked.



Example:



{

&#x20; "action": "kubectl delete pod payment-api",

&#x20; "approved": false

}



The system returns a blocked status instead of executing the action.



**Safety Model**



The safety workflow is:



LOW-RISK ACTION

&#x20;     |

&#x20;     v

Approval Not Required

&#x20;     |

&#x20;     v

Simulated Execution





HIGH-RISK ACTION

&#x20;     |

&#x20;     v

Human Approval Required

&#x20;     |

&#x20;     +-------------------+

&#x20;     |                   |

&#x20;     v                   v

&#x20;  APPROVED             DENIED

&#x20;     |                   |

&#x20;     v                   v

&#x20; SIMULATED             BLOCKED

&#x20; EXECUTION



The current MVP does not execute real destructive Kubernetes or production infrastructure operations.



All remediation execution is simulated.



Incident Example



The sample incident is:



Incident: INC-001

Service: payment-api

Severity: P1

Related Alerts

ALT-001 - HighMemoryUsage

ALT-002 - PodRestarting

ALT-003 - HTTP5xx

Incident Assessment



The payment-api service is experiencing:



High memory usage

Pod instability

Elevated HTTP 500 errors

Root Cause



The most likely root cause is a memory-related failure associated with deployment v2.4.1.



The application was deployed at:



2026-09-10T10:25:00



Memory usage increased after the deployment and the container was subsequently terminated with OOMKilled.



Evidence

Deployment: v2.4.1

Memory Events: 2

OOM Events: 1

HTTP Error Events: 1

Confidence: High

Impact



The payment-api service experienced elevated HTTP 500 errors.



The HTTP 500 error rate increased to approximately 35%, and the payment-api pod experienced a restart.



Incident Timeline

2026-09-10T10:25:00

Deployment v2.4.1 released to payment-api



2026-09-10T10:30:00

Memory usage exceeded 90%



2026-09-10T10:31:00

payment-api pod restarted



2026-09-10T10:32:00

HTTP 500 error rate increased to 35%



2026-09-10T10:33:00

Triage Agent correlated 3 alerts into INC-001



2026-09-10T10:34:00

Diagnostic Agent identified likely OOMKilled failure



2026-09-10T10:35:00

Remediation Agent generated a safe remediation plan



2026-09-10T10:36:00

Safety Gate protected destructive actions with human approval



2026-09-10T10:37:00

Blameless RCA generated for INC-001

Blameless RCA



The system generates a blameless Root Cause Analysis containing:



Incident Summary

Impact

Timeline

Root Cause

Prevention

Incident Summary



The payment-api service experienced a P1 incident involving high memory usage, pod instability, and elevated HTTP 500 errors.



**Impact**



HTTP 500 error rates increased to approximately 35%, and the payment-api pod experienced a restart.



**Root Cause**



The most likely root cause was a memory-related failure associated with deployment v2.4.1.



Memory usage increased after the deployment and the container was subsequently terminated with OOMKilled.



**Prevention**



Recommended prevention measures include:



Add memory regression testing before production deployment

Review Kubernetes resource requests and limits

Improve memory monitoring and alerting

Add deployment health checks

Document rollback procedures





**API Endpoints**



The FastAPI application provides the following endpoints:



GET  /health

GET  /incident

GET  /alerts

GET  /rca

GET  /timeline

POST /approve

Health Check



Endpoint:



GET /health



Example:



{

&#x20; "status": "healthy"

}



**Incident Endpoint**



Endpoint:



GET /incident



This endpoint returns:



Incident information

Incident severity

Related alerts

Diagnosis

Root cause

Evidence

Recommended remediation

Agent execution status

Current incident status



**Alerts Endpoint**



Endpoint:



GET /alerts



Returns the available incident alerts used by the system.



**RCA Endpoint**



Endpoint:



GET /rca



Returns the generated Root Cause Analysis.



**Timeline Endpoint**



Endpoint:



GET /timeline



Returns the incident timeline and related events.



**Approval Endpoint**



Endpoint:



POST /approve



Used to process Human-in-the-Loop approval for high-risk remediation actions.



Example request:



{

&#x20; "action": "Roll back deployment v2.4.1 to v2.4.0",

&#x20; "approved": true

}



**Dashboard**



The project includes a web dashboard that displays the complete incident response lifecycle.



The dashboard provides:



System status

Incident overview

Alert correlation

Agent execution status

Root cause diagnosis

Remediation plan

Risk classification

Human approval status

Incident timeline

Blameless RCA



The dashboard communicates with the FastAPI backend through REST API endpoints.



**Installation**



**1. Clone the Repository**

git clone https://github.com/koushikpoojary/sre-incident-agent.git

cd sre-incident-agent



**2. Create Virtual Environment**

python -m venv venv



**3. Activate Virtual Environment**



On Windows:



venv\\Scripts\\activate



**4. Install Dependencies**

pip install -r requirements.txt



**Running the Application**



Start the FastAPI server:



venv\\Scripts\\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000



The API will be available at:



http://127.0.0.1:8000

Testing the API



**Health Check**

curl http://127.0.0.1:8000/health



Expected response:



{

&#x20; "status": "healthy"

}

**Get Incident**

curl http://127.0.0.1:8000/incident

**Get Alerts**

curl http://127.0.0.1:8000/alerts

**Get Timeline**

curl http://127.0.0.1:8000/timeline

**Get RCA**

curl http://127.0.0.1:8000/rca



**Test Human Approval**

curl -X POST http://127.0.0.1:8000/approve -H "Content-Type: application/json" -d "{\\"action\\":\\"Roll back deployment v2.4.1 to v2.4.0\\",\\"approved\\":true}"



**Technologies Used**



Python

FastAPI

Uvicorn

JavaScript

HTML

CSS

JSON

Git

GitHub



**Current MVP Scope**



This project is currently an MVP.



The current implementation uses:



Simulated incident data

Simulated logs

Simulated deployment information

Simulated remediation execution

Human approval for high-risk actions



The system is intended to demonstrate the architecture and governance model of a multi-agent SRE incident response system.



It does not directly execute destructive production infrastructure commands.



**Safety and Governance**



The project follows a safety-first approach to automated incident response.



The system separates:



Investigation

Diagnosis

Remediation planning

Safety evaluation

Human approval

Execution



This prevents potentially destructive actions from being executed without explicit approval.



**Future Improvements**



Possible future extensions include:



Integration with real Kubernetes clusters

Real-time monitoring and alert ingestion

Prometheus and Grafana integration

Real application log collection

Automated deployment comparison

Real remediation execution with additional safeguards

Authentication and authorization

Persistent incident history

Audit logging

Slack or email notifications

More advanced agent reasoning and tool integration





**Project Goal**



The goal of this project is to demonstrate a governed multi-agent approach to SRE incident response.



The system combines automated incident investigation, root cause diagnosis, remediation planning, safety controls, Human-in-the-Loop approval, simulated execution, and blameless RCA generation.

