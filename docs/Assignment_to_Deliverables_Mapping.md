# StockMind - Assignment-to-Deliverables Mapping

## Assignment 1.1 - Project Ideation, Environment Modeling and PEAS
- Persona: StockMind Inventory Manager Agent.
- Domain: simulated retail warehouse inventory and supplier replenishment.
- PEAS: Performance, Environment, Actuators and Sensors defined in the design PDF.
- Environment classification: partially observable, stochastic, sequential, dynamic, discrete, multi-agent and partially known.
- Agent vs OOP: compares autonomous goal-directed action selection with a conventional method-driven OOP implementation.
- Submission: `Assignment_1.1_Design_Specification.pdf`.

## Assignment 1.2 - Rule-Based Environmental Reasoner
- File: `stockmind/reflex_agent.py`.
- Percepts: SKU, current stock, reorder level and target stock.
- Condition-action rules: zero stock, low stock, normal stock and overstock.
- Log: `logs/assignment_1_2_reflex_execution.txt`.

## Assignment 2.1 - Concurrent Task Daemonization
- File: `stockmind/monitor.py`.
- One daemon thread periodically reads an inventory snapshot.
- `queue.Queue` safely transfers snapshot events to the main process.
- `threading.Event` stops the worker; `time.perf_counter()` records measured scan latency.
- Log: `logs/assignment_2_1_concurrency_latency.txt`.

## Assignment 2.2 - Distributed Agent Messaging
- Files: `stockmind/socket_server.py`, `stockmind/socket_client.py`, `stockmind/protocol.py`, `run_supplier.py`, `run_buyer.py`.
- Transport: TCP socket, local port 5055.
- Serialization: newline-delimited JSON object.
- Typed messages: `RESTOCK_REQUEST` and `SUPPLIER_QUOTE`.
- Security: message envelopes are signed and verified with Ed25519 keys.
- Evidence: `logs/assignment_2_2_agent_a_client.txt` and `logs/assignment_2_2_agent_b_server.txt`.

## Assignment 3.1 - Multi-Agent Coordination Protocol
- File: `stockmind/negotiation.py`.
- Agents: buyer and supplier with maximum/minimum reservation prices.
- Protocol: bounded alternating offers and counteroffers, acceptance when both reservation constraints overlap, and no-agreement handling if they do not overlap.
- Timeline: `logs/assignment_3_1_negotiation_timeline.txt`.

## Assignment 3.2 - Self-Interested Agent Utility Optimization
- Files: `stockmind/utility.py` (`UtilityOptimizerAgent`) and `stockmind/agent_manager.py`.
- Formula: `U = 0.40*C + 0.25*D + 0.20*R + 0.15*Q`.
- Feasibility checks: required quantity, maximum unit budget and maximum delivery days.
- Dataset: ten supplier offers in `data/supplier_offers.json`.
- Evidence: `logs/assignment_3_2_utility_results.txt` and `.csv`.

## Assignment 4.1 - Belief-Desire-Intention Modeling
- File: `stockmind/bdi.py`.
- Beliefs hold current stock, reorder level, supplier availability and delivery risk.
- Desires represent strategic goals such as avoiding stockouts and minimizing cost.
- Intentions are explicit action pipelines.
- Replanning changes the first intention from requesting quotes to finding an alternative supplier when the current supplier becomes unavailable.
- Evidence: `logs/assignment_4_1_bdi_replanning.txt` and `tests/test_bdi.py`.

## Assignment 4.2 - Knowledge Representation and Adaptive API Integration
- Files: `stockmind/weather_api.py`, `config/agent_config.json`, `data/knowledge_base.json`.
- External REST source: Open-Meteo Forecast API.
- JSON parser extracts precipitation probability and precipitation, classifies a configurable delivery-risk level, and the main `StockMindAgent` applies the observation to BDI beliefs and replans.
- Evidence: run `python main.py api` or use the dashboard Live API tab. The build container could not resolve the external API host, so its generated log records the failed network attempt honestly. The parser is tested using a local fixture in `tests/test_weather_parse.py`.

## Assignment 5.1 - Agent Authentication and Host Integrity Verification
- File: `stockmind/security.py`.
- Ed25519 digital signatures; trusted public-key registry; timestamp validation; nonce replay protection.
- Tests include valid signature, modified payload, unknown sender and replayed nonce.
- Evidence: `logs/assignment_5_1_security_verification.txt` and `tests/test_security.py`.

## Assignment 5.2 - Capstone Consolidation and Secure Deployment
- Integrated orchestrator: `stockmind/agent_manager.py` (`StockMindAgent` connects environment perception, reflex reasoning, BDI replanning and utility optimization).
- Integrated UI: `app.py` (Streamlit).
- CLI: `main.py`.
- Architecture: `assets/architecture.png`.
- Presentation script: `3_Minute_Presentation_Script.md`.
- Slide outline: `Presentation_Slide_Outline.md`.
- Test suite: `tests/`.
- GitHub preparation: `GITHUB_SETUP.md`.
- A video file is not pre-recorded: the student should screen-record the running dashboard and terminals using the supplied presentation script.
