# Drone Security Analyst

A prototype AI system for automated drone-based property security monitoring. The system combines simulated drone video frames and telemetry, VLM-based structured observation extraction, temporal context management, security-event detection, SQLite indexing, vehicle tracking, and a natural-language Security Analyst Agent.

## 1. Overview

The Drone Security Analyst processes simulated drone observations and telemetry to identify security-relevant events across multiple frames.

### Example

**Input**

```text
A blue Ford F150 is entering through the main gate.
```

**AI observation**

```json
{
  "objects": [
    {
      "type": "vehicle",
      "color": "blue",
      "make": "Ford",
      "model": "F150",
      "activity": "entering",
      "confidence": 0.95
    }
  ]
}
```

The resulting context can then be queried using natural language:

```text
How many times did the Ford enter?
```

Example answer:

```text
The blue Ford F150 entered the property twice.
```

---

## 2. Features

### Core Features

- Simulated drone video frames
- Simulated drone telemetry
- OpenRouter-based VLM analysis
- Structured observation extraction
- Frame-level SQLite indexing
- Temporal context management
- Person loitering detection
- Security alert generation
- Vehicle event tracking
- Natural-language security queries

### Example Security Event

```text
PERSON_LOITERING
```

```text
Severity: HIGH
Location: main_gate
Duration: 5 seconds
```

---

## 3. System Architecture

```text
Video + Telemetry
        |
        v
Frame/Telemetry Matching
        |
        v
       VLM
        |
        v
Structured Observation
        |
        +------------------+
        |                  |
        v                  v
   SQLite Index     Context Manager
                           |
                           v
                    Vehicle Tracker
                           |
                           v
                     Alert Engine
                           |
                           v
                Security Analyst Agent
                           |
                           v
                  Natural Language Answer
```

See `docs/architecture.md` for the detailed architecture.

---

## 4. Project Structure

```text
drone-security-analyst/
|
├── src/
│   ├── agent/
│   │   └── security_agent.py
│   │
│   ├── context/
│   │   ├── context_manager.py
│   │   └── vehicle_tracker.py
│   │
│   ├── database/
│   │   ├── db.py
│   │   └── repository.py
│   │
│   ├── retrieval/
│   │   └── frame_retriever.py
│   │
│   ├── vision/
│   │   ├── vlm_analyzer.py
│   │   └── test_vlm.py
│   │
│   ├── alerts/
│   │   └── alert_engine.py
│   │
│   ├── frame_simulator.py
│   ├── telemetry_simulator.py
│   └── main.py
│
├── data/
│
├── tests/
│
├── docs/
│   ├── architecture.md
│   ├── testing.md
│   └── ai-tools.md
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

> The exact tree may differ slightly depending on the current implementation. Update filenames in this section if the repository structure changes.

---

## 5. Environment Setup

### Clone the repository

```bash
git clone <PRIVATE_REPOSITORY_URL>
cd drone-security-analyst
```

### Create a virtual environment

```bash
python -m venv myenv
```

### Windows

```powershell
myenv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure OpenRouter

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_key
```

Do not commit `.env` or API keys to Git.

---

## 6. Run the Application

From the project root:

```bash
python -m src.main
```

The application processes the simulated frames and telemetry and generates:

- VLM observations
- Indexed frames
- Temporal context
- Vehicle events
- Security alerts
- Natural-language security queries

After processing, the Security Analyst Agent allows questions about the observed security events.

---

## 7. Example Input

The prototype uses the following simulated frame descriptions:

```text
Frame 1:
A blue Ford F150 is entering through the main gate.

Frame 2:
A person is standing near the main gate.

Frame 3:
The same person is still standing near the main gate.

Frame 4:
The person remains standing near the main gate.

Frame 5:
The person is leaving the main gate area.

Frame 6:
The blue Ford F150 is leaving the property.

Frame 7:
The blue Ford F150 is entering through the main gate again.
```

---

## 8. Example Output

### Vehicle Events

```text
00:00 | main_gate | blue Ford F150 | entering
00:09 | main_gate | blue Ford F150 | exiting
00:12 | main_gate | blue Ford F150 | entering
```

### Loitering Event

```text
Event Type: PERSON_LOITERING
Object Type: person
Location: main_gate
First Seen: 00:01
Last Seen: 00:06
Duration: 5 seconds
Frames Observed: 3
```

### Alert

```text
Alert Type: PERSON_LOITERING
Severity: HIGH
Location: main_gate
```

---

## 9. Natural-Language Security Queries

After processing the frames, the Security Analyst Agent can be queried with questions such as:

```text
Was the blue Ford F150 seen more than once?
```

```text
What vehicles entered the property?
```

```text
Was there any security alert?
```

```text
What happened at the main gate?
```

```text
How many times did the Ford enter?
```

The agent answers using the structured security context rather than directly querying raw video frames.

---

## 10. AI Tools Used

AI-assisted development tools were used throughout the prototype development process. They were primarily used for:

- Architecture brainstorming
- Code scaffolding
- Debugging
- Prompt refinement
- Test-case generation
- Documentation assistance

For the VLM component, AI assistance was used to design the structured observation schema and security-analysis prompt. Generated code was reviewed and modified during implementation rather than being treated as a black box.

During debugging, AI assistance helped identify issues related to:

- OpenRouter configuration
- Response handling
- Temporal context expiration
- Database integration
- Security-agent integration

---

## 11. Testing

Run the test suite from the project root:

```bash
pytest
```

The test suite covers core components such as:

- Context management
- Database functionality
- Simulation components

The project should be tested after changes to the processing pipeline to ensure that existing functionality remains intact.

---

## 12. Limitations

The current prototype uses **simulated frame descriptions rather than a live drone camera feed**. Therefore, the VLM perception stage demonstrates the structured reasoning and event-processing pipeline but does not benchmark real-world object-detection accuracy.

The current temporal identity tracking is simplified and should be replaced with a dedicated multi-object tracking system in a production deployment.

The current VLM stage also processes text descriptions. A production system would connect the pipeline to actual video frames and a vision-capable model.

---

## 13. Future Improvements

A production-oriented version could extend the current architecture as follows:

```text
Live RTSP Camera
        |
        v
OpenCV Frame Sampling
        |
        v
Object Detection
        |
        v
Multi-Object Tracking
        |
        v
VLM Event Understanding
        |
        v
Vector + Metadata Retrieval
        |
        v
Multi-Drone Event Correlation
        |
        v
Real-Time Alerting
```

Potential improvements include:

- Live RTSP video ingestion
- YOLO/object detection
- ByteTrack or DeepSORT
- Improved VLM
- PostgreSQL
- Vector database
- Redis/Kafka
- Multi-drone support
- Video summarization
- Web dashboard
- Push/SMS/email alerts
- Human-in-the-loop alert confirmation

---

## 14. Development Status

The project currently demonstrates an end-to-end prototype for:

```text
Simulated Drone Data
        ↓
Structured AI Observations
        ↓
Temporal Context
        ↓
Security Events
        ↓
Alerts
        ↓
Natural-Language Security Analysis
```

The next major step is connecting the prototype to real drone video and telemetry sources.
