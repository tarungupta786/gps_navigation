"""Network Connectivity Monitor - educational Computer Networks PBL project."""
from __future__ import annotations

import csv
import os
import platform
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
HISTORY_FILE = DATA_DIR / "monitor_history.csv"
OUTAGE_FILE = DATA_DIR / "outage_log.csv"
HISTORY_COLUMNS = [
    "timestamp", "host", "mode", "status", "latency_ms", "packet_loss_pct",
    "http_status", "check_details"
]
OUTAGE_COLUMNS = ["timestamp", "host", "event", "details", "outage_started", "duration_seconds"]
DEFAULT_HOSTS = "google.com\nexample.com\n1.1.1.1"

st.set_page_config(page_title="Network Connectivity Monitor", page_icon="🌐", layout="wide")


def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        pd.DataFrame(columns=HISTORY_COLUMNS).to_csv(HISTORY_FILE, index=False)
    if not OUTAGE_FILE.exists():
        pd.DataFrame(columns=OUTAGE_COLUMNS).to_csv(OUTAGE_FILE, index=False)


def parse_host(value: str) -> str:
    """Accept a hostname, IP address, or URL and return the host part."""
    value = value.strip()
    if not value:
        return ""
    if "://" in value:
        parsed = urlparse(value)
        return parsed.hostname or ""
    # Remove a possible path from entries such as example.com/status.
    return value.split("/", 1)[0].strip()


def http_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if not re.match(r"^https?://", value, flags=re.IGNORECASE):
        value = "https://" + value
    return value


def run_ping(host: str, count: int = 4, timeout_seconds: int = 2) -> dict:
    """Run the system ping command and return success, latency, loss and details."""
    if not host:
        return {"ok": False, "latency_ms": None, "packet_loss_pct": 100.0, "details": "Invalid or empty host"}

    system = platform.system().lower()
    if system == "windows":
        command = ["ping", "-n", str(count), "-w", str(timeout_seconds * 1000), host]
    else:
        # Linux/macOS use -W in seconds on Linux; on macOS -W uses milliseconds.
        if system == "darwin":
            command = ["ping", "-c", str(count), "-W", str(timeout_seconds * 1000), host]
        else:
            command = ["ping", "-c", str(count), "-W", str(timeout_seconds), host]

    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=(count * timeout_seconds + 3), check=False
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        output = (completed.stdout or "") + "\n" + (completed.stderr or "")
        # Some ping implementations return a non-zero exit code when only some
        # requests receive replies. Treat any received reply as reachable.
        received_match = re.search(r"(\d+)\s+received", output, re.IGNORECASE)
        windows_received = re.search(r"Received\s*=\s*(\d+)", output, re.IGNORECASE)
        has_reply_line = bool(re.search(r"time[=<]\s*[\d.]+\s*ms", output, re.IGNORECASE))
        received_count = int(received_match.group(1)) if received_match else 0
        if windows_received:
            received_count = max(received_count, int(windows_received.group(1)))
        ok = completed.returncode == 0 or received_count > 0 or has_reply_line

        # Parse average latency where the platform reports it.
        latency = None
        avg_match = re.search(r"(?:average|avg)\s*[=:]\s*([\d.]+)\s*ms", output, re.IGNORECASE)
        if avg_match:
            latency = float(avg_match.group(1))
        else:
            unix_match = re.search(r"(?:rtt|round-trip).*?=\s*[\d.]+/([\d.]+)/", output, re.IGNORECASE)
            if unix_match:
                latency = float(unix_match.group(1))
            else:
                times = [float(x) for x in re.findall(r"time[=<]\s*([\d.]+)\s*ms", output, re.IGNORECASE)]
                if times:
                    latency = sum(times) / len(times)
                elif ok:
                    latency = round(elapsed_ms / max(count, 1), 2)

        loss = 0.0 if ok else 100.0
        loss_match = re.search(r"([\d.]+)%\s*(?:packet\s*)?loss", output, re.IGNORECASE)
        if loss_match:
            loss = float(loss_match.group(1))
        elif system == "windows":
            sent_recv = re.search(r"Packets:.*?Sent\s*=\s*(\d+).*?Received\s*=\s*(\d+)", output, re.IGNORECASE | re.DOTALL)
            if sent_recv:
                sent, received = int(sent_recv.group(1)), int(sent_recv.group(2))
                loss = round((sent - received) * 100 / sent, 2) if sent else 100.0

        detail = "Ping response received" if ok else "No ping response (host may be offline or ICMP may be blocked)"
        if completed.returncode != 0 and output.strip():
            # Keep diagnostics concise for the dashboard.
            detail += ". " + " ".join(output.strip().split())[-180:]
        return {"ok": ok, "latency_ms": round(latency, 2) if latency is not None else None,
                "packet_loss_pct": loss, "details": detail}
    except FileNotFoundError:
        return {"ok": False, "latency_ms": None, "packet_loss_pct": None,
                "details": "Ping command not found on this system"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "latency_ms": None, "packet_loss_pct": 100.0, "details": "Ping timed out"}
    except Exception as exc:  # Keep one failed host from stopping all monitoring.
        return {"ok": False, "latency_ms": None, "packet_loss_pct": None, "details": f"Ping error: {exc}"}


def run_http_check(value: str, timeout_seconds: int = 4) -> dict:
    """Check whether a web server responds over HTTP/HTTPS."""
    url = http_url(value)
    if not url:
        return {"ok": False, "latency_ms": None, "http_status": None, "details": "Invalid or empty URL"}
    started = time.perf_counter()
    try:
        response = requests.get(
            url, timeout=timeout_seconds, allow_redirects=True,
            headers={"User-Agent": "NetworkConnectivityMonitor-PBL/1.0"}
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        # Any HTTP response means the server was reachable, including 4xx/5xx responses.
        return {"ok": True, "latency_ms": round(elapsed_ms, 2), "http_status": response.status_code,
                "details": f"HTTP response received (status {response.status_code})"}
    except requests.RequestException as exc:
        return {"ok": False, "latency_ms": None, "http_status": None,
                "details": f"HTTP request failed: {type(exc).__name__}"}


def load_csv(path: Path, columns: list[str]) -> pd.DataFrame:
    try:
        if path.exists():
            frame = pd.read_csv(path)
            for column in columns:
                if column not in frame.columns:
                    frame[column] = None
            return frame[columns]
    except (pd.errors.EmptyDataError, OSError, pd.errors.ParserError):
        pass
    return pd.DataFrame(columns=columns)


def record_outage_events(host: str, status: str, timestamp: str, details: str) -> None:
    history = load_csv(HISTORY_FILE, HISTORY_COLUMNS)
    previous = history[history["host"] == host]
    previous_status = str(previous.iloc[-1]["status"]) if not previous.empty else None
    events = load_csv(OUTAGE_FILE, OUTAGE_COLUMNS)

    if status == "DOWN" and previous_status != "DOWN":
        new_event = {"timestamp": timestamp, "host": host, "event": "OUTAGE STARTED",
                     "details": details, "outage_started": timestamp, "duration_seconds": None}
        events = pd.concat([events, pd.DataFrame([new_event])], ignore_index=True)
    elif status == "UP" and previous_status == "DOWN":
        prior_outages = events[(events["host"] == host) & (events["event"] == "OUTAGE STARTED")]
        outage_start = str(prior_outages.iloc[-1]["outage_started"]) if not prior_outages.empty else ""
        duration = None
        try:
            duration = round((pd.to_datetime(timestamp) - pd.to_datetime(outage_start)).total_seconds(), 2)
        except (ValueError, TypeError):
            pass
        new_event = {"timestamp": timestamp, "host": host, "event": "RECOVERED",
                     "details": details, "outage_started": outage_start, "duration_seconds": duration}
        events = pd.concat([events, pd.DataFrame([new_event])], ignore_index=True)
    events.to_csv(OUTAGE_FILE, index=False)


def check_host(entry: str, mode: str, count: int, timeout: int) -> dict:
    host = parse_host(entry)
    if not host:
        return {"host": entry, "status": "DOWN", "latency_ms": None, "packet_loss_pct": None,
                "http_status": None, "check_details": "Invalid or empty host"}

    ping_result = None
    http_result = None
    if mode in ("Ping", "Ping + HTTP"):
        ping_result = run_ping(host, count=count, timeout_seconds=timeout)
    if mode in ("HTTP", "Ping + HTTP"):
        # Keep any explicitly supplied URL/path for the HTTP check.
        http_result = run_http_check(entry, timeout_seconds=max(timeout, 2))

    successes = []
    latencies = []
    details = []
    packet_loss = None
    http_status = None
    if ping_result is not None:
        successes.append(ping_result["ok"])
        details.append("Ping: " + ping_result["details"])
        packet_loss = ping_result.get("packet_loss_pct")
        if ping_result.get("latency_ms") is not None:
            latencies.append(ping_result["latency_ms"])
    if http_result is not None:
        successes.append(http_result["ok"])
        details.append("HTTP: " + http_result["details"])
        http_status = http_result.get("http_status")
        if http_result.get("latency_ms") is not None:
            latencies.append(http_result["latency_ms"])

    # For combined mode, either a successful ping or HTTP response means the host is reachable.
    is_up = any(successes)
    return {"host": host, "status": "UP" if is_up else "DOWN",
            "latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
            "packet_loss_pct": packet_loss, "http_status": http_status,
            "check_details": " | ".join(details)}


def run_monitoring(entries: list[str], mode: str, count: int, timeout: int) -> pd.DataFrame:
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    results = []
    for entry in entries:
        if not entry.strip():
            continue
        result = check_host(entry, mode, count, timeout)
        row = {"timestamp": now, "host": result["host"], "mode": mode,
               "status": result["status"], "latency_ms": result["latency_ms"],
               "packet_loss_pct": result["packet_loss_pct"], "http_status": result["http_status"],
               "check_details": result["check_details"]}
        record_outage_events(result["host"], result["status"], now, result["check_details"])
        results.append(row)
    if results:
        old = load_csv(HISTORY_FILE, HISTORY_COLUMNS)
        updated = pd.concat([old, pd.DataFrame(results)], ignore_index=True)
        updated = updated.tail(10000)
        updated.to_csv(HISTORY_FILE, index=False)
    return pd.DataFrame(results)


ensure_data_files()
st.title("🌐 Network Connectivity Monitor")
st.caption("Computer Networks PBL • Monitor host availability, latency, packet loss, and outages.")

with st.sidebar:
    st.header("Monitor settings")
    hosts_text = st.text_area("Hosts to monitor (one per line)", value=DEFAULT_HOSTS, height=125,
                              help="Enter a hostname, IP address, or URL. Example: google.com")
    mode = st.selectbox("Check method", ["Ping", "HTTP", "Ping + HTTP"], index=2,
                        help="Ping checks ICMP reachability. HTTP checks whether a web server responds.")
    ping_count = st.slider("Ping requests per host", min_value=1, max_value=6, value=3,
                           help="Used only when Ping is selected.")
    timeout = st.slider("Timeout (seconds)", min_value=1, max_value=8, value=2)
    auto_refresh = st.checkbox("Auto-refresh every 30 seconds", value=False)
    st.caption("Checks run only when you press the button, or when auto-refresh is enabled.")
    run_clicked = st.button("▶ Run connectivity check", type="primary", use_container_width=True)
    clear_confirm = st.checkbox("I understand this deletes saved monitoring history")
    if st.button("Clear history and outage log", use_container_width=True):
        if clear_confirm:
            pd.DataFrame(columns=HISTORY_COLUMNS).to_csv(HISTORY_FILE, index=False)
            pd.DataFrame(columns=OUTAGE_COLUMNS).to_csv(OUTAGE_FILE, index=False)
            st.session_state.pop("last_results", None)
            st.success("Saved history and outage log cleared.")
        else:
            st.warning("Tick the confirmation checkbox before clearing saved data.")

if auto_refresh:
    try:
        from streamlit_autorefresh import st_autorefresh
        refresh_count = st_autorefresh(interval=30_000, key="network_monitor_refresh")
        last_refresh_count = st.session_state.get("last_refresh_count", -1)
        if refresh_count != last_refresh_count:
            run_clicked = True
            st.session_state["last_refresh_count"] = refresh_count
    except ImportError:
        st.warning("Auto-refresh needs streamlit-autorefresh. Install the packages in requirements.txt.")

entries = list(dict.fromkeys(line.strip() for line in hosts_text.splitlines() if line.strip()))
if run_clicked:
    if not entries:
        st.error("Enter at least one host in the sidebar.")
    else:
        with st.spinner(f"Checking {len(entries)} host(s)…"):
            st.session_state["last_results"] = run_monitoring(entries, mode, ping_count, timeout)
        st.toast("Connectivity check complete", icon="✅")

results = st.session_state.get("last_results", pd.DataFrame(columns=HISTORY_COLUMNS))
if not results.empty:
    up_count = int((results["status"] == "UP").sum())
    down_count = int((results["status"] == "DOWN").sum())
    latency_values = pd.to_numeric(results["latency_ms"], errors="coerce").dropna()
    avg_latency = f"{latency_values.mean():.2f} ms" if not latency_values.empty else "—"
else:
    history_now = load_csv(HISTORY_FILE, HISTORY_COLUMNS)
    latest_rows = history_now.sort_values("timestamp").groupby("host", as_index=False).tail(1) if not history_now.empty else history_now
    up_count = int((latest_rows["status"] == "UP").sum()) if not latest_rows.empty else 0
    down_count = int((latest_rows["status"] == "DOWN").sum()) if not latest_rows.empty else 0
    latency_values = pd.to_numeric(latest_rows["latency_ms"], errors="coerce").dropna() if not latest_rows.empty else pd.Series(dtype=float)
    avg_latency = f"{latency_values.mean():.2f} ms" if not latency_values.empty else "—"

m1, m2, m3, m4 = st.columns(4)
m1.metric("Hosts UP", up_count)
m2.metric("Hosts DOWN", down_count, delta_color="inverse")
m3.metric("Average response time", avg_latency)
m4.metric("Hosts entered", len(entries))

st.subheader("Latest connectivity results")
if results.empty:
    st.info("Enter your hosts in the sidebar and select **Run connectivity check** to see live results. The figures above use saved history when available.")
else:
    display = results[["host", "status", "latency_ms", "packet_loss_pct", "http_status", "check_details"]].copy()
    display.columns = ["Host", "Status", "Latency (ms)", "Packet loss (%)", "HTTP status", "Details"]
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.download_button("Download latest results (CSV)", results.to_csv(index=False).encode("utf-8"),
                       file_name="latest_connectivity_results.csv", mime="text/csv")

history = load_csv(HISTORY_FILE, HISTORY_COLUMNS)
outages = load_csv(OUTAGE_FILE, OUTAGE_COLUMNS)

left, right = st.columns([1.5, 1])
with left:
    st.subheader("Response-time history")
    if not history.empty:
        chart_data = history.copy()
        chart_data["timestamp"] = pd.to_datetime(chart_data["timestamp"], errors="coerce")
        chart_data["latency_ms"] = pd.to_numeric(chart_data["latency_ms"], errors="coerce")
        chart_data = chart_data.dropna(subset=["timestamp", "latency_ms"])
        if not chart_data.empty:
            chart_data = chart_data.sort_values("timestamp").tail(500)
            chart_data["time"] = chart_data["timestamp"].dt.strftime("%H:%M:%S")
            pivot = chart_data.pivot_table(index="time", columns="host", values="latency_ms", aggfunc="last")
            st.line_chart(pivot, y_label="Milliseconds")
        else:
            st.info("No successful latency measurements have been recorded yet.")
    else:
        st.info("A response-time graph will appear after your first check.")
with right:
    st.subheader("Latest host status")
    if not history.empty:
        latest = history.sort_values("timestamp").groupby("host", as_index=False).tail(1)
        for _, row in latest.iterrows():
            icon = "🟢" if row["status"] == "UP" else "🔴"
            st.write(f"{icon} **{row['host']}** — {row['status']}")
            st.caption(f"Last checked: {row['timestamp']}")
    else:
        st.info("No saved checks yet.")

st.subheader("Outage log")
if outages.empty:
    st.info("Outages and recoveries will be logged here when a host changes status between checks.")
else:
    st.dataframe(outages.sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)
    st.download_button("Download outage log (CSV)", outages.to_csv(index=False).encode("utf-8"),
                       file_name="outage_log.csv", mime="text/csv")

with st.expander("How to interpret the results"):
    st.markdown(
        "- **UP:** At least one selected check succeeded. In Ping + HTTP mode, either a ping reply or an HTTP response is enough.\n"
        "- **DOWN:** All selected checks failed. A host may still be running but block ping requests or reject connections.\n"
        "- **Latency:** Ping response time or HTTP request duration, depending on the selected method. In combined mode, successful measurements are averaged.\n"
        "- **Packet loss:** Estimated from ping replies only; it is not calculated by the HTTP check.\n"
        "- **HTTP status:** A returned HTTP status (including 404 or 500) still confirms that an HTTP server responded.\n"
        "- **Outage log:** Status transitions are detected only when checks are run; it is not a 24/7 background monitoring service."
    )

st.divider()
st.caption("Educational project only. Use hosts you are authorized to test. Monitoring data is stored locally in the project's data/ folder.")
