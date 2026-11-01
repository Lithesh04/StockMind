# StockMind Submission Deliverable Status

## Included and prepared in this project folder

- [x] Assignment 1.1 PEAS, domain, environment classification and Agent-vs-OOP design PDF.
- [x] Assignment 1.2 commented Python reflex agent and execution log.
- [x] Assignment 2.1 background thread, safe queue, stop event and measured latency log.
- [x] Assignment 2.2 TCP socket server/client, JSON message protocol, signed messages and actual local dual-process terminal logs.
- [x] Assignment 3.1 separate BuyerAgent and SupplierAgent classes, alternating-offer implementation and negotiation timeline.
- [x] Assignment 3.2 utility formula, 10 supplier offers, hard constraints, computed CSV and text results.
- [x] Assignment 4.1 BDI classes, belief update, replan behavior and intention-shift test/log.
- [x] Assignment 4.2 REST API request module, JSON parser, knowledge representation, parser test and API procedure.
- [x] Assignment 5.1 Ed25519 signature module, trusted-peer verification, tamper/replay/unknown-sender tests and logs.
- [x] Assignment 5.2 integrated StockMindAgent, Streamlit dashboard source, CLI demo, architecture PNG, test suite and three-minute recording script.

## Must be completed on the student's computer

1. **Live API execution:** The code calls the live Open-Meteo endpoint, but the build environment used to prepare this ZIP could not resolve `api.open-meteo.com`. Run `python main.py api` on a computer with internet access and retain the generated `logs/assignment_4_2_live_api.txt`. The JSON parser test is included and is not falsely labelled as live data.
2. **Actual presentation video:** A real screen recording must be made while the dashboard and terminals run on the student's computer. Use `docs/3_Minute_Presentation_Script.md` and `docs/Video_Recording_Procedure.md`. A fabricated recording is not included.
3. **GitHub repository URL:** The source is prepared for publishing, but it has not been pushed to a GitHub account. Follow `docs/GITHUB_SETUP.md` and submit the real URL after pushing.

## Verification performed while preparing this package

- Automated test suite: 12 passed.
- Python syntax compilation: passed.
- Local TCP buyer/supplier exchange: executed successfully on `127.0.0.1:5055`.
- PDF design specification: rendered and visually checked at 120 DPI.
- Streamlit app: source compiled successfully. Streamlit is listed in `requirements.txt`; the dashboard must be installed and launched on the student's computer.
