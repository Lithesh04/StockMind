# StockMind - 3-Minute Demonstration Script

**Before recording:** Open the `StockMind` folder in VS Code, activate `.venv`, run `python main.py setup`, start the dashboard with `python -m streamlit run app.py`, and open the local Streamlit URL. Keep a second VS Code terminal available. For the socket segment, start `python run_supplier.py` in Terminal 1 and `python run_buyer.py` in Terminal 2. Stop the supplier server after the exchange.

## 0:00-0:20 - Introduction
"This is StockMind, an autonomous multi-agent inventory management and supply-chain optimization prototype. It monitors stock, detects shortages, coordinates with suppliers, negotiates offers and recommends replenishment decisions. The inventory and supplier prices are simulated; the weather feed is a real API when connected."

## 0:20-0:40 - Assignment 1: Perception and reflex rules
Open **Inventory & Rules**. Point out Rice and Milk at or below reorder level. Click **Run condition-action rules**. Explain that the agent senses current stock and triggers condition-action rules to calculate the replenishment quantity.

## 0:40-1:00 - Assignment 2.1: Background worker
Open **Concurrency** and click **Start background monitor**. Explain that a daemon thread polls inventory and sends snapshots through a thread-safe queue while the main app remains responsive. Point to the measured scan latency.

## 1:00-1:20 - Assignment 2.2: Socket communication
Show the two terminal logs or run the two-terminal exchange live. Explain that Agent A sends a typed JSON restock request over TCP and Agent B returns a signed quotation.

## 1:20-1:40 - Assignment 3.1: Negotiation
Open **Negotiation** and click **Run negotiation protocol**. Explain the buyer's maximum price, seller's minimum price, counteroffers and agreement.

## 1:40-2:00 - Assignment 3.2: Utility optimization
Open **Supplier Optimization** and click **Evaluate 10 supplier offers**. Explain the weighted utility function and hard constraints. Show the calculated winner and rejected offers.

## 2:00-2:20 - Assignment 4.1: BDI replanning
Open **BDI Planner** and click **Run BDI intention-change scenario**. Explain beliefs, desires and intentions. A supplier availability belief changes, so the agent cancels its old plan and searches for an alternative supplier.

## 2:20-2:40 - Assignment 4.2: External API
Open **Live API** and click **Fetch live weather forecast**. Explain that the agent parses precipitation data from Open-Meteo and uses it as a simple delivery-risk input. If the network is unavailable, state that the endpoint requires internet and show the parser test instead of claiming a live result.

## 2:40-2:55 - Assignment 5.1: Security
Open **Security** and click **Run security verification tests**. Show a trusted signed request accepted, while a replay, modified payload and unknown sender are rejected.

## 2:55-3:00 - Conclusion
"StockMind combines reflex reasoning, concurrent monitoring, socket communication, multi-agent negotiation, utility optimization, BDI replanning, external knowledge and cryptographic message verification in one integrated project. Purchases remain subject to human approval."

## Recording checklist
- Capture the dashboard clearly at 1080p if possible.
- Keep text readable; zoom browser to 90-100%.
- Show the two terminals during socket communication.
- Do not display private key files or commit them to GitHub.
- Do not claim simulated stock or supplier quotations are live data.
