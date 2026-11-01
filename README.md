# StockMind - Autonomous Multi-Agent Inventory Management System

**Project title:** StockMind: An Autonomous Multi-Agent Inventory Monitoring and Supply Chain Optimization System  
**Language:** Python  
**Interface:** Streamlit dashboard + command-line demonstrations  
**Academic scope:** Assignments 1.1 through 5.2

StockMind monitors a simulated warehouse, detects low stock with condition-action rules, runs background monitoring, communicates with a supplier agent over TCP sockets, negotiates replenishment terms, ranks 10 supplier offers using a weighted utility function, maintains Belief-Desire-Intention (BDI) state, consumes an external weather API, and authenticates agent messages using Ed25519 signatures.

> **Important scope note:** Inventory and supplier offers are simulated academic data. The Open-Meteo weather forecast is a real external API integration when the computer has internet access. The weather signal is used as a simple configurable delivery-risk heuristic; it is not a real courier-delay prediction. No real purchase or payment is made. A human must approve any purchase recommendation.

---

## 1. What is included

| Assignment | Included implementation | Evidence |
|---|---|---|
| 1.1 | Persona, problem, PEAS, environment classification, Agent vs OOP comparison | `docs/Assignment_1.1_Design_Specification.pdf` |
| 1.2 | Simple reflex condition-action engine | `stockmind/reflex_agent.py`, `stockmind/agent_manager.py`, `logs/assignment_1_2_reflex_execution.txt` |
| 2.1 | Threaded polling worker, `queue.Queue`, stop event and latency measurement | `stockmind/monitor.py`, `logs/assignment_2_1_concurrency_latency.txt` |
| 2.2 | TCP client/server, typed JSON messages, signed requests and replies | `run_supplier.py`, `run_buyer.py`, `logs/assignment_2_2_*.txt` |
| 3.1 | Buyer-supplier alternating-offer negotiation | `stockmind/negotiation.py`, `logs/assignment_3_1_negotiation_timeline.txt` |
| 3.2 | Weighted utility model, hard constraints and 10-offer evaluation | `stockmind/utility.py`, `logs/assignment_3_2_utility_results.csv` |
| 4.1 | Beliefs, desires, intentions and dynamic replanning | `stockmind/bdi.py`, `logs/assignment_4_1_bdi_replanning.txt` |
| 4.2 | Open-Meteo REST integration and JSON parser | `stockmind/weather_api.py`, `logs/assignment_4_2_api_status.txt` |
| 5.1 | Ed25519 signatures, trusted sender check, tamper and replay checks | `stockmind/security.py`, `logs/assignment_5_1_security_verification.txt` |
| 5.2 | Integrated Streamlit dashboard, architecture schematic and recording script | `app.py`, `assets/architecture.png`, `docs/3_Minute_Presentation_Script.md` |

## 2. Requirements

- Windows 10/11, macOS or Linux
- Python 3.10 or newer (Python 3.11/3.12 recommended)
- VS Code
- Internet connection only for the live weather API assignment

## 3. Open the complete project in VS Code

1. Download and extract `StockMind_Project.zip`.
2. Open VS Code.
3. Select **File -> Open Folder**.
4. Choose the extracted `StockMind` folder (the folder that contains `app.py`, `main.py` and `requirements.txt`).
5. In VS Code, open **Terminal -> New Terminal**.

Do not open only an individual `.py` file. Open the whole `StockMind` folder so imports and relative paths work.

## 4. First-time setup (Windows PowerShell)

Run these commands in the VS Code terminal, one at a time:

```powershell
python --version
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py setup
```

If PowerShell blocks virtual-environment activation, run this once in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Then install requirements and run setup again if needed.

**Command Prompt alternative:**

```cmd
.venv\Scripts\activate.bat
```

## 5. Run the final web dashboard

With the virtual environment activated:

```powershell
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. Open that URL in your browser. The dashboard has tabs for Overview, Inventory & Rules, Concurrency, Supplier Optimization, Negotiation, BDI Planner, Live API, Security, and Presentation & Deliverables.

For the final presentation, open the **Presentation & Deliverables** tab and click **Run complete StockMind demo**. Use the other tabs to show each feature individually.

## 6. Run the command-line demonstrations

```powershell
python main.py demo
```

This runs the rule engine, background worker, negotiation, utility ranking, BDI replanning and security checks. It writes fresh execution logs into `logs/`.

Run automated tests:

```powershell
python -m pytest -q
```

or:

```powershell
python main.py test
```

## 7. Run the two-terminal socket demonstration (Assignment 2.2)

**First-time setup is required:** run `python main.py setup` once to generate local demo signing keys.

1. In VS Code choose **Terminal -> New Terminal**.
2. Terminal 1:

```powershell
python run_supplier.py
```

3. Keep Terminal 1 running. Open a second terminal using the plus (+) button.
4. Terminal 2:

```powershell
python run_buyer.py
```

5. Observe Agent A sending a signed restock request, Agent B authenticating it and returning a signed supplier quote. The buyer verifies the supplier's signature.
6. Stop the supplier server with `Ctrl+C` in Terminal 1.

The default local host/port is `127.0.0.1:5055`.

## 8. Run the live external API demonstration (Assignment 4.2)

With internet access:

```powershell
python main.py api
```

Or open the dashboard's **Live API** tab and click **Fetch live weather forecast**. The default coordinates are a sample Chennai warehouse location. You can change them in the UI.

The API endpoint is Open-Meteo Forecast API: `https://api.open-meteo.com/v1/forecast`. The code requests hourly precipitation probability and precipitation, parses the JSON and classifies a configurable delivery-risk level. Open-Meteo documentation: https://open-meteo.com/en/docs

If the API request fails, check your internet connection and try again. Do not submit a fabricated live response; show the actual error or re-run on a working network. Unit tests use a local sample payload only to test parsing.

## 9. Where to find each deliverable

- Design PDF: `docs/Assignment_1.1_Design_Specification.pdf`
- Full mapping: `docs/Assignment_to_Deliverables_Mapping.md`
- Architecture diagram: `assets/architecture.png`
- Presentation script: `docs/3_Minute_Presentation_Script.md`
- Slide outline: `docs/Presentation_Slide_Outline.md`
- GitHub publishing steps: `docs/GITHUB_SETUP.md`
- Generated execution logs: `logs/`
- Test suite: `tests/`

## 10. GitHub repository submission

This folder is ready to publish, but it has not been uploaded to a GitHub account. Follow `docs/GITHUB_SETUP.md` to create your own repository and push the source. Do not commit private keys from `data/keys/`; `.gitignore` excludes them.

## 11. Troubleshooting

**`ModuleNotFoundError`**: Confirm VS Code opened the full `StockMind` folder and that the virtual environment is activated. Re-run `pip install -r requirements.txt`.

**`streamlit` is not recognized**: Run `python -m streamlit run app.py`.

**Port 5055 already in use**: Close any older Supplier Agent terminal or change the port in `run_supplier.py` and `run_buyer.py` consistently.

**Live API request fails**: The API section requires internet access. Other features work with local demonstration data.

**Private key missing**: Run `python main.py setup`. Keys are created locally and should not be shared.

## 12. Academic honesty and scope

This is a demonstrable educational prototype. The warehouse stock, supplier quotes, supplier negotiations and offer data are simulated. The utility scores are computed from the included data and formula. The weather feed is external and real only when a live request succeeds. The project does not place real orders, process payments, or claim to control a real warehouse.

## 13. Main source layout

```text
StockMind/
  app.py                       Streamlit presentation dashboard
  main.py                      CLI setup, demo, API and test commands
  run_supplier.py               Supplier Agent TCP server
  run_buyer.py                  Buyer Agent TCP client
  stockmind/
    agent_manager.py            Integrated capstone buyer agent
    environment.py              Warehouse state and simulated telemetry
    reflex_agent.py             Condition-action reasoner
    monitor.py                  Background thread and queue
    socket_server.py            Supplier socket endpoint
    socket_client.py            Buyer socket endpoint
    protocol.py                 JSON-over-TCP framing
    negotiation.py              BuyerAgent / SupplierAgent bargaining
    utility.py                  Self-interested utility optimizer
    bdi.py                      Beliefs, desires, intentions and replanning
    weather_api.py              Open-Meteo request and JSON parser
    security.py                 Ed25519 signatures and replay checks
    database.py                 SQLite event history
  config/                       Agent settings and trusted peer map
  data/                         Inventory, offers and knowledge JSON
  tests/                        Automated tests for the core capabilities
  logs/                         Assignment console and test evidence
  docs/                         Assignment PDF, mapping and presentation guides
  assets/architecture.png       Architecture schematic
```

## 14. Recording the 3-minute video

Follow `docs/Video_Recording_Procedure.md` and `docs/3_Minute_Presentation_Script.md`. The project contains the recording procedure and script, but the actual screen recording must be captured on your computer while the dashboard and terminal are running.
