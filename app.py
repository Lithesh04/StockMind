"""StockMind web dashboard. Start with: streamlit run app.py"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from stockmind.environment import InventoryEnvironment
from stockmind.reflex_agent import ReflexAgent
from stockmind.demo import (load_offers, run_bdi_demo, run_security_demo, run_all_demos)
from stockmind.monitor import InventoryMonitor
from stockmind.agent_manager import StockMindAgent
from stockmind.bdi import BDIEngine
from stockmind.weather_api import fetch_weather
from stockmind.database import EventStore

st.set_page_config(page_title="StockMind | Autonomous Inventory Agent", page_icon="📦", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2.5rem;}
.hero {padding: 1.25rem 1.5rem; border-radius: 14px; background: linear-gradient(115deg,#13243a,#1e4e63); color: white; margin-bottom: 1rem;}
.hero h1 {margin: 0; color: white; font-size: 2.1rem;}
.hero p {margin: .35rem 0 0 0; color: #d8e8f2;}
.small-muted {color: #6b7280; font-size: .86rem;}
</style>
<div class="hero"><h1>📦 StockMind</h1><p>Autonomous inventory monitoring, supplier coordination and replenishment optimization</p></div>
""", unsafe_allow_html=True)

env = InventoryEnvironment(ROOT / "data" / "inventory.json")
store = EventStore(ROOT / "data" / "stockmind.db")

products = env.list_products()
low_count = sum(p["current_stock"] <= p["reorder_level"] for p in products)
critical_count = sum(p["current_stock"] == 0 for p in products)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Products monitored", len(products))
m2.metric("Low-stock items", low_count)
m3.metric("Critical stockouts", critical_count)
m4.metric("Agent mode", "Simulation / Approval")
st.caption("Academic prototype: supplier offers and purchases are simulated. Open-Meteo weather data is live when the API tab is run.")

tabs = st.tabs(["Overview", "Inventory & Rules", "Concurrency", "Supplier Optimization", "Negotiation", "BDI Planner", "Live API", "Security", "Presentation & Deliverables"])

with tabs[0]:
    st.subheader("Inventory overview")
    df = pd.DataFrame(products)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.subheader("Agent's current observations")
    scan = ReflexAgent().scan(products)
    alert_df = pd.DataFrame([x for x in scan if x["severity"] != "OK"])
    if alert_df.empty:
        st.success("No current low-stock rules are triggered.")
    else:
        st.warning(f"{len(alert_df)} inventory rule(s) require attention.")
        st.dataframe(alert_df[["product", "stock", "reorder_level", "rule", "action", "reorder_quantity"]], use_container_width=True, hide_index=True)
    st.info("The agent recommends replenishment. A human must approve simulated purchase orders.")

with tabs[1]:
    st.subheader("Inventory environment and reflex reasoning")
    st.dataframe(pd.DataFrame(products), use_container_width=True, hide_index=True)
    names = {p["product"]: p["sku"] for p in products}
    selected = st.selectbox("Choose a product to simulate a stock update", list(names))
    col1, col2 = st.columns([1, 2])
    with col1:
        new_stock = st.number_input("New stock quantity", min_value=0, max_value=10000, value=int(env.get_product(names[selected])["current_stock"]))
        if st.button("Apply stock update", type="primary"):
            changed = env.update_stock(names[selected], int(new_stock))
            store.add_event("STOCK_UPDATE", json.dumps(changed))
            st.success(f"Updated {changed['product']}: {changed['old_stock']} → {changed['new_stock']}")
    with col2:
        if st.button("Run condition-action rules"):
            rules = ReflexAgent().scan(env.list_products())
            st.session_state["reflex_results"] = rules
            store.add_event("REFLEX_SCAN", json.dumps({"products_scanned": len(rules)}))
        if "reflex_results" in st.session_state:
            st.dataframe(pd.DataFrame(st.session_state["reflex_results"]), use_container_width=True, hide_index=True)
    st.markdown("**Rule set:** zero stock → urgent replenishment; stock at/below reorder level → create request; stock above target → overstock review; otherwise → continue monitoring.")

with tabs[2]:
    st.subheader("Concurrent background worker")
    st.write("The monitor runs independently in a daemon thread, places snapshots in a thread-safe `queue.Queue`, and does not wait for a scan before returning control to this dashboard.")
    if "monitor_worker" not in st.session_state:
        st.session_state["monitor_worker"] = InventoryMonitor(
            lambda: InventoryEnvironment(ROOT / "data" / "inventory.json").list_products(), interval_seconds=3.0)
        st.session_state["monitor_events"] = []
    worker = st.session_state["monitor_worker"]
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Start background worker", type="primary"):
            worker.start()
            store.add_event("MONITOR_START", "Background monitor started")
    with c2:
        if st.button("Stop background worker"):
            worker.stop()
            store.add_event("MONITOR_STOP", "Background monitor stopped")
    with c3:
        if st.button("Refresh worker events"):
            st.session_state["monitor_events"].extend(worker.read_events())
    st.metric("Worker status", "RUNNING" if worker.thread and worker.thread.is_alive() else "STOPPED")
    if st.session_state["monitor_events"]:
        event_rows = []
        for event in st.session_state["monitor_events"][-20:]:
            if event["type"] == "INVENTORY_SNAPSHOT":
                low_items = [p["product"] for p in event["items"] if p["current_stock"] <= p["reorder_level"]]
                event_rows.append({"scan": event["scan"], "items": len(event["items"]), "latency_ms": round(event["latency_ms"], 3), "low_stock_products": ", ".join(low_items) or "None"})
            else:
                event_rows.append({"scan": "ERROR", "items": "", "latency_ms": "", "low_stock_products": event.get("error", "Unknown error")})
        st.dataframe(pd.DataFrame(event_rows), use_container_width=True, hide_index=True)
    st.caption("Start is non-blocking. Wait a few seconds, then click Refresh worker events to retrieve queued snapshots.")

with tabs[3]:
    st.subheader("Supplier offer comparison and utility optimization")
    st.markdown("**Utility:** U = 0.40 × Cost + 0.25 × Delivery + 0.20 × Reliability + 0.15 × Quality")
    qty = st.number_input("Required quantity", min_value=1, value=50)
    budget = st.number_input("Maximum unit budget (₹)", min_value=1.0, value=60.0, step=1.0)
    max_days = st.number_input("Maximum delivery days", min_value=1, value=7)
    if st.button("Evaluate 10 supplier offers", type="primary"):
        from stockmind.utility import evaluate_offers
        result = evaluate_offers(load_offers(), int(qty), float(budget), int(max_days))
        st.session_state["utility_result"] = result
        store.add_event("UTILITY_EVALUATION", json.dumps({"winner": result["winner"]["supplier"] if result["winner"] else None, "feasible": result["feasible_count"]}))
    if "utility_result" in st.session_state:
        result = st.session_state["utility_result"]
        display = pd.DataFrame(result["evaluated"])
        st.dataframe(display[["offer_id", "supplier", "unit_price", "available_qty", "delivery_days", "reliability_pct", "quality_rating", "utility_score", "feasible", "rejection_reasons"]], use_container_width=True, hide_index=True)
        x, y, z = st.columns(3)
        x.metric("Offers evaluated", len(result["evaluated"]))
        y.metric("Feasible offers", result["feasible_count"])
        z.metric("Rejected offers", result["rejected_count"])
        if result["winner"]:
            st.success(f"Selected: {result['winner']['supplier']} — utility {result['winner']['utility_score']:.2f}/100 — ₹{result['winner']['unit_price']:.2f} per unit")
        else:
            st.error("No supplier offer meets all mandatory constraints.")

with tabs[4]:
    st.subheader("Buyer and supplier negotiation")
    buyer_max = st.number_input("Buyer's maximum price (₹ / unit)", min_value=1.0, value=52.0)
    supplier_min = st.number_input("Supplier's minimum price (₹ / unit)", min_value=1.0, value=48.0)
    if st.button("Run negotiation protocol", type="primary"):
        from stockmind.negotiation import negotiate
        result = negotiate(float(buyer_max), float(supplier_min), rounds=6, buyer_start=46.0, supplier_start=54.0)
        st.session_state["negotiation_result"] = result
        store.add_event("NEGOTIATION", json.dumps(result))
    if "negotiation_result" in st.session_state:
        result = st.session_state["negotiation_result"]
        st.dataframe(pd.DataFrame(result["timeline"]), use_container_width=True, hide_index=True)
        if result["agreement"]:
            st.success(f"Negotiation agreement: ₹{result['agreed_price']:.2f} per unit")
        else:
            st.warning("No agreement: buyer's maximum is below supplier's minimum.")

with tabs[5]:
    st.subheader("Belief-Desire-Intention cognitive layer")
    st.write("Update a belief and trigger plan recalculation. This demonstrates an intention shift when a supplier becomes unavailable.")
    if st.button("Run BDI intention-change scenario", type="primary"):
        st.session_state["bdi_log"] = run_bdi_demo()
        store.add_event("BDI_REPLAN", st.session_state["bdi_log"].replace("\n", " | "))
    if "bdi_log" in st.session_state:
        st.code(st.session_state["bdi_log"], language="text")
    with st.expander("Inspect BDI model concepts"):
        st.json({"beliefs": ["current_stock", "reorder_level", "supplier_available", "delivery_risk"],
                 "desires": ["avoid_stockout", "minimize_replenishment_cost"],
                 "intentions": ["request_supplier_quotes", "rank_feasible_offers", "negotiate_best_offer", "request_human_purchase_approval"]})

with tabs[6]:
    st.subheader("Live external API - Open-Meteo")
    st.write("Weather forecast is used as a configurable delivery-risk signal. It is not a courier-delay prediction.")
    lat = st.number_input("Warehouse latitude", value=13.0827, format="%.4f")
    lon = st.number_input("Warehouse longitude", value=80.2707, format="%.4f")
    if st.button("Fetch live weather forecast", type="primary"):
        with st.spinner("Requesting forecast from Open-Meteo..."):
            try:
                weather = fetch_weather(float(lat), float(lon))
                st.session_state["weather"] = weather
                capstone_agent = StockMindAgent(ROOT / "data" / "inventory.json", ROOT / "data" / "supplier_offers.json")
                capstone_agent.perceive_and_reason()
                replanned_intentions = capstone_agent.apply_weather_observation(weather)
                st.session_state["weather_replanned_intentions"] = replanned_intentions
                store.add_event("WEATHER_API", json.dumps(weather))
            except Exception as exc:
                st.error(f"API request failed: {exc}")
    if "weather" in st.session_state:
        weather = st.session_state["weather"]
        a, b, c = st.columns(3)
        a.metric("Max precipitation probability", f"{weather['max_precipitation_probability_pct']:.0f}%")
        b.metric("Max hourly precipitation", f"{weather['max_hourly_precipitation_mm']:.1f} mm")
        c.metric("Delivery-risk rule", weather["delivery_risk"])
        st.json(weather)
        if "weather_replanned_intentions" in st.session_state:
            st.markdown("**BDI intentions after weather belief update**")
            st.write(st.session_state["weather_replanned_intentions"])
    st.caption("API endpoint and current parameters are documented in stockmind/weather_api.py. Internet access is required for this tab.")

with tabs[7]:
    st.subheader("Agent authentication and message integrity")
    st.write("Ed25519 signed envelopes are checked against trusted public keys. Tests include unknown senders, tampering and replayed nonces.")
    if st.button("Run security verification tests", type="primary"):
        try:
            st.session_state["security_log"] = run_security_demo()
            store.add_event("SECURITY_TEST", st.session_state["security_log"].replace("\n", " | "))
        except Exception as exc:
            st.session_state["security_log"] = f"Security setup failed: {exc}"
    if "security_log" in st.session_state:
        st.code(st.session_state["security_log"], language="text")
    st.warning("The demo keys are for local coursework only. Do not reuse them in production.")

with tabs[8]:
    st.subheader("Presentation mode - end-to-end walkthrough")
    st.markdown("Use this screen during the final demonstration. Each section below corresponds to one or more assignment deliverables.")
    st.image(str(ROOT / "assets" / "architecture.png"), caption="StockMind system architecture", use_container_width=True)
    if st.button("Run complete StockMind demo", type="primary"):
        result = run_all_demos(include_live_api=False)
        st.session_state["full_demo"] = result["text"]
        store.add_event("FULL_DEMO", "Core demo executed; live API is a separate button in the API tab.")
    if "full_demo" in st.session_state:
        st.code(st.session_state["full_demo"], language="text")
    checklist = pd.DataFrame([
        ["1.1", "PEAS + environment + Agent vs OOP", "docs/Assignment_1.1_Design_Specification.pdf"],
        ["1.2", "Reflex rules + console log", "stockmind/reflex_agent.py + logs/assignment_1_2_reflex_execution.txt"],
        ["2.1", "Threaded worker + latency log", "stockmind/monitor.py + logs/assignment_2_1_concurrency_latency.txt"],
        ["2.2", "TCP sockets + signed JSON message", "run_supplier.py + run_buyer.py"],
        ["3.1", "Buyer-supplier negotiation timeline", "stockmind/negotiation.py + logs/assignment_3_1_negotiation_timeline.txt"],
        ["3.2", "Utility formula + 10 offer CSV", "stockmind/utility.py + logs/assignment_3_2_utility_results.csv"],
        ["4.1", "BDI + intention shift test", "stockmind/bdi.py + logs/assignment_4_1_bdi_replanning.txt"],
        ["4.2", "Live REST API + JSON parsing", "stockmind/weather_api.py + logs/assignment_4_2_live_api.txt (created when API succeeds)"],
        ["5.1", "Ed25519 authentication + rejection tests", "stockmind/security.py + logs/assignment_5_1_security_verification.txt"],
        ["5.2", "Integrated UI + architecture + video script", "app.py + assets/architecture.png + docs/3_Minute_Presentation_Script.md"],
    ], columns=["Assignment", "What to demonstrate", "Evidence"])
    st.dataframe(checklist, use_container_width=True, hide_index=True)
    pdf_file = ROOT / "docs" / "Assignment_1.1_Design_Specification.pdf"
    if pdf_file.exists():
        st.download_button("Download Assignment 1.1 Design PDF", data=pdf_file.read_bytes(),
                           file_name=pdf_file.name, mime="application/pdf")
    st.markdown("**Socket demonstration:** Run `python run_supplier.py` in VS Code Terminal 1, then `python run_buyer.py` in Terminal 2. The previous verified local exchange is shown below as evidence.")
    for log_name in ["assignment_2_2_agent_a_client.txt", "assignment_2_2_agent_b_server.txt"]:
        log_file = ROOT / "logs" / log_name
        if log_file.exists():
            with st.expander(log_name):
                st.code(log_file.read_text(encoding="utf-8"), language="text")
    st.markdown("**Recording tip:** Use the included 3-minute script and keep this dashboard open while switching tabs to show each capability.")
    st.markdown("**Project event history**")
    st.dataframe(pd.DataFrame(store.latest_events(20)), use_container_width=True, hide_index=True)

st.divider()
st.caption("StockMind educational prototype | Python + Streamlit | All purchases require human approval")
