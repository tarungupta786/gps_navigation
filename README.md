# Network Connectivity Monitor

A beginner-friendly Computer Networks PBL built with Python and Streamlit. It checks multiple hosts, displays reachability and response time, estimates ping packet loss, records status changes, and plots response-time history.

## Features

- Monitor multiple hostnames, IP addresses, or URLs
- Ping, HTTP, or combined checks
- UP/DOWN status and response latency
- Ping packet-loss estimate
- HTTP status-code display
- Response-time history graph
- Outage-start and recovery log with estimated duration
- CSV downloads for latest results and outage history
- Optional 30-second auto-refresh
- Local CSV storage under `data/`

## Requirements

- Python 3.10 or newer recommended
- Internet connection for public hosts
- A working system `ping` command for ping checks (some networks block ICMP)

## Run on Windows

1. Install Python from https://www.python.org/downloads/ if it is not already installed. During installation, enable **Add Python to PATH**.
2. Extract this project ZIP into a folder.
3. Open Command Prompt in that folder.
4. Create and activate a virtual environment (recommended):

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```

5. Install dependencies:

   ```bat
   pip install -r requirements.txt
   ```

6. Start the app:

   ```bat
   streamlit run app.py
   ```

7. Streamlit will show a local address, normally `http://localhost:8501`. Open it in your browser.
8. In the left sidebar, edit the host list and click **Run connectivity check**.

## Run on Linux or macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## How to use

1. Enter one host per line, for example `google.com`, `example.com`, or `1.1.1.1`.
2. Choose **Ping**, **HTTP**, or **Ping + HTTP**.
3. Set the ping count and timeout.
4. Click **Run connectivity check**.
5. Review the latest results, response-time graph, host status, and outage log.
6. Download results as CSV if needed.

## Networking concepts demonstrated

- IP addressing and hostnames
- ICMP Echo Request / Echo Reply (ping)
- HTTP/HTTPS request-response behavior
- Latency and approximate packet loss
- Host availability and basic troubleshooting
- Logging and monitoring history

## Important interpretation notes

- A failed ping does not necessarily mean a website is down. Firewalls and servers may block ICMP. Use **HTTP** or **Ping + HTTP** for web servers.
- An HTTP status such as 404 or 500 still means the server responded; it does not mean the page content is healthy.
- In combined mode, a host is marked UP if either ping or HTTP succeeds.
- Outage transitions are detected only when the app performs checks. Auto-refresh is optional; this is not a guaranteed always-on monitoring daemon.
- Measurements vary with the network, DNS, firewall rules, and host load.

## Data files

The app creates these files automatically:

- `data/monitor_history.csv` — one row for each host check
- `data/outage_log.csv` — outage start and recovery events

Use the **Clear history and outage log** control in the sidebar to reset saved records. The app does not send monitoring history to a separate database.

## Troubleshooting

- **`streamlit` is not recognized:** activate the virtual environment and run `python -m streamlit run app.py`.
- **Ping command not found:** install/enable the operating system ping utility or use HTTP checks.
- **Every ping fails:** try HTTP mode; your network or target may block ICMP.
- **HTTP request fails:** check the URL, internet connection, DNS, proxy, or certificate configuration.
- **Port 8501 is busy:** run `streamlit run app.py --server.port 8502`.

## Project structure

```text
network_connectivity_monitor/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    ├── monitor_history.csv
    └── outage_log.csv
```
