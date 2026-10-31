# Network Connectivity Monitor

A beginner-friendly **Computer Networks Project-Based Learning (PBL)** application built with **Python, Streamlit, Pandas, and Requests**. It checks whether selected hosts are reachable, measures response time, estimates packet loss from ping results, records availability changes, and displays monitoring history in a web dashboard.

> **Project type:** Educational network-monitoring simulator/application  
> **Primary subject:** Computer Networks  
> **Interface:** Local web dashboard  
> **Storage:** CSV files on the computer running the application

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Objectives](#3-objectives)
4. [Features](#4-features)
5. [How It Works](#5-how-it-works)
6. [Networking Concepts](#6-networking-concepts)
7. [Technology Stack](#7-technology-stack)
8. [Requirements](#8-requirements)
9. [Installation and Setup](#9-installation-and-setup)
10. [How to Use the Application](#10-how-to-use-the-application)
11. [Understanding the Results](#11-understanding-the-results)
12. [Data Storage](#12-data-storage)
13. [Testing](#13-testing)
14. [Negative Testing](#14-negative-testing)
15. [Troubleshooting](#15-troubleshooting)
16. [Project Structure](#16-project-structure)
17. [Limitations](#17-limitations)
18. [Future Enhancements](#18-future-enhancements)
19. [Conclusion](#19-conclusion)

---

## 1. Project Overview

The Network Connectivity Monitor is an application that helps a user check the reachability of websites, servers, and IP addresses from their own computer. Instead of repeatedly running commands manually, the user can enter a list of hosts and view the results in one dashboard.

The application supports three check methods:

- **Ping:** Uses the operating system's `ping` command to test ICMP reachability.
- **HTTP:** Sends an HTTP/HTTPS request to check whether a web server responds.
- **Ping + HTTP:** Runs both types of checks. A host is considered `UP` if at least one of the selected checks succeeds.

The dashboard presents host status, response-time measurements, ping packet-loss estimates, HTTP status codes, response-time history, and detected outage/recovery events.

## 2. Problem Statement

Network users may experience slow connections, unavailable servers, DNS problems, or websites that do not respond. Checking multiple hosts individually can be inconvenient, and it may be difficult to keep a record of when a host became unavailable or recovered.

This project provides a simple, centralized dashboard to perform basic connectivity checks, show diagnostic information, and save check history locally for review.

## 3. Objectives

- Check the reachability of multiple hostnames, IP addresses, and URLs.
- Demonstrate ping and HTTP/HTTPS request-response behavior.
- Measure and display response time (latency).
- Estimate packet loss using ping results where the operating system provides usable output.
- Display HTTP response status codes.
- Maintain local monitoring history and an outage/recovery log.
- Visualize response-time history using a graph.
- Export recent results and outage records to CSV files.
- Practice basic network troubleshooting and negative testing.

## 4. Features

### 4.1 Multiple-host monitoring
Enter one hostname, IP address, or URL per line. The application removes blank entries and avoids duplicate entries in a single check.

Examples:

```text
google.com
example.com
1.1.1.1
https://www.python.org
```

### 4.2 Multiple check methods

| Method | What it tests | Main result |
|---|---|---|
| Ping | ICMP reachability using the system ping utility | Reply status, approximate latency, packet-loss estimate |
| HTTP | Whether an HTTP/HTTPS server responds | Response duration and HTTP status code |
| Ping + HTTP | Both ping and HTTP checks | `UP` if either selected check succeeds |

### 4.3 Dashboard metrics
The dashboard summarizes the number of hosts marked `UP`, the number marked `DOWN`, the average available response-time measurement, and the number of hosts entered.

### 4.4 Response-time history
Successful measurements are saved and displayed in a line chart. This can help the user compare response times over multiple checks.

### 4.5 Outage and recovery log
When a host's recorded status changes from `UP` to `DOWN`, the app can record an outage-start event. If a later check changes the status from `DOWN` to `UP`, it records a recovery event and attempts to calculate the elapsed duration.

**Important:** These events are detected only when checks run. The app is not a guaranteed 24/7 background monitoring service.

### 4.6 CSV export
The user can download the latest check results and the outage log for a report or further analysis in spreadsheet software.

### 4.7 Optional automatic refresh
The sidebar includes an option to refresh and run checks every 30 seconds. This feature requires the `streamlit-autorefresh` package. If the package is not installed, the app displays a warning and manual checking remains available.

### 4.8 Clear saved history
The application can clear its local monitoring history and outage log. It requires the user to tick a confirmation checkbox before deletion.

---

## 5. How It Works

1. The user enters hosts in the sidebar.
2. The user selects Ping, HTTP, or Ping + HTTP and configures the ping count and timeout.
3. The user clicks **Run connectivity check** (or enables automatic refresh).
4. For Ping, Python starts the operating system's ping command and reads its output.
5. For HTTP, the application sends an HTTP/HTTPS request and records whether a response was received, its status code, and the request duration.
6. The app combines the selected check results into an `UP` or `DOWN` status.
7. Results are displayed in the dashboard and appended to local CSV history.
8. Status changes can be added to the outage log, and latency measurements are plotted when available.

### Simplified workflow

```text
User enters hosts
       |
       v
Select check method and settings
       |
       v
Run Ping and/or HTTP checks
       |
       v
Collect response, latency, loss, and HTTP status
       |
       v
Determine UP or DOWN status
       |
       v
Display results and update CSV history
       |
       v
Update chart and outage/recovery log
```

---

## 6. Networking Concepts

### IP address and hostname
An IP address identifies a network interface/address used for communication. A hostname such as `example.com` is a human-readable name that typically must be resolved through DNS before a connection can be made.

### ICMP and ping
Ping commonly sends ICMP Echo Requests and waits for Echo Replies. The result can help assess whether a destination responds to this kind of network test. Firewalls and servers may block ICMP, so failed ping does not conclusively prove that a host or website is offline.

### HTTP and HTTPS
HTTP is an application-layer protocol used for web communication. HTTPS is HTTP protected by TLS. The application sends a request and checks whether the server returns an HTTP response.

### Latency
Latency is the time taken for a check to complete or a response to be received, measured in milliseconds. In this project, ping latency is parsed from system output where possible. HTTP latency is the elapsed time for the HTTP request.

### Packet loss
Packet loss is the proportion of ping requests that do not receive replies. The app attempts to read packet-loss information from the operating system's ping output. Results may vary by operating system and ping implementation. HTTP checks do not calculate packet loss.

### Availability and troubleshooting
A status of `UP` means at least one selected test succeeded. A status of `DOWN` means the selected test or tests failed. Possible causes include a host being offline, a DNS problem, a blocked protocol, a timeout, or a local internet connection issue.

---

## 7. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and connectivity checks |
| Streamlit | Interactive browser-based dashboard |
| Pandas | Read, update, and analyze CSV monitoring data |
| Requests | Send HTTP/HTTPS requests |
| `subprocess` | Run the operating system's ping command |
| `socket` / URL parsing utilities | Standard-library networking and input handling utilities where applicable |
| CSV | Local persistence and downloadable reports |

No separate database server is required.

## 8. Requirements

- Python **3.10 or newer** is recommended.
- Internet access is needed to check public internet hosts.
- A working system `ping` command is required for Ping mode. Some networks may block ICMP.
- A modern web browser.
- The Python dependencies listed in `requirements.txt`.

---

## 9. Installation and Setup

### Windows (Command Prompt or PowerShell)

1. Install Python from [python.org](https://www.python.org/downloads/). During installation, enable **Add Python to PATH** if that option is shown.
2. Extract the project ZIP.
3. Open a terminal in the extracted project folder (the folder containing `app.py`).
4. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

5. Activate it in Command Prompt:

   ```bat
   .venv\Scripts\activate
   ```

   Or activate it in PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

6. Install the dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Start the application:

   ```bash
   streamlit run app.py
   ```

8. Open the local URL printed in the terminal. It is commonly `http://localhost:8501`.

### Linux or macOS

From the project folder, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit in your browser.

### Stop the application
Return to the terminal where Streamlit is running and press `Ctrl+C`.

---

## 10. How to Use the Application

1. Launch the app and open it in your browser.
2. In the sidebar, locate **Hosts to monitor (one per line)**.
3. Enter one or more hosts, for example `google.com`, `example.com`, or `1.1.1.1`.
4. Choose the **Check method**:
   - **Ping** to test ICMP responses.
   - **HTTP** to test a web server.
   - **Ping + HTTP** to run both checks.
5. Set **Ping requests per host** if using Ping mode. This setting is ignored by HTTP-only checks.
6. Set the timeout in seconds.
7. Click **Run connectivity check**.
8. Review the summary metrics and the **Latest connectivity results** table.
9. Review the response-time history chart and outage log after several checks.
10. Use the download buttons to save the latest results or outage log as CSV.
11. To enable automatic checks, select **Auto-refresh every 30 seconds**. Keep in mind this is a browser-session-based convenience, not a dedicated monitoring service.
12. To clear local records, tick the confirmation checkbox and then click **Clear history and outage log**.

### Suggested first demonstration

Use these entries for an initial demo:

```text
google.com
example.com
1.1.1.1
```

Select **Ping + HTTP** and run the check. Results depend on your internet connection, DNS configuration, firewall, and whether the target allows ping or HTTP requests.

---

## 11. Understanding the Results

| Field | Meaning |
|---|---|
| Host | Normalized hostname or IP address checked by the app |
| Status | `UP` if at least one selected check succeeds; otherwise `DOWN` |
| Latency (ms) | Ping response time or HTTP request duration; combined mode averages the successful measurements collected |
| Packet loss (%) | Estimate derived from ping output only; may be unavailable if the system output cannot be parsed |
| HTTP status | HTTP status code returned by the web server, if any |
| Details | Short diagnostic message describing the result of each selected check |

### Interpreting HTTP codes

- `200` generally indicates a successful HTTP response.
- `301` or `302` indicates a redirect (the request may follow redirects automatically).
- `404` indicates that the requested page was not found, but the server did respond.
- `500` indicates a server-side error response, but it still proves an HTTP server returned a response.

For a connectivity monitor, receiving an HTTP response—even a 4xx or 5xx status—means the web server was reachable at the HTTP layer. It does not necessarily mean the requested page or application is functioning correctly.

### Interpreting a DOWN result

A `DOWN` result means the selected test(s) failed. It does not always mean the entire device is offline. Possible reasons include:

- The hostname does not exist or DNS lookup failed.
- The destination is offline or unreachable from the current network.
- ICMP ping is blocked while HTTP may still work.
- HTTP/HTTPS connections are blocked or refused.
- A timeout occurred.
- The local computer has no internet access.

---

## 12. Data Storage

The application creates a `data/` directory automatically when it starts.

### `data/monitor_history.csv`
Stores individual host-check records, including:

- timestamp
- host
- check method
- status
- latency in milliseconds
- packet-loss estimate
- HTTP status code
- diagnostic details

The application retains up to the most recent 10,000 rows in this file when new results are saved.

### `data/outage_log.csv`
Stores detected status-change events, including:

- event timestamp
- host
- event type (`OUTAGE STARTED` or `RECOVERED`)
- diagnostic details
- outage start time
- estimated duration in seconds when it can be calculated

Monitoring records are stored locally in CSV files; they are not automatically sent to a separate project database. Back up the `data/` folder if you want to keep your records.

---

## 13. Testing

Testing checks whether the application behaves as expected under normal conditions.

| Test ID | Input / action | Expected result |
|---|---|---|
| T01 | Check a valid, reachable website using HTTP | HTTP response and status code are displayed |
| T02 | Check a reachable host using Ping | Ping result is displayed if ICMP replies are allowed |
| T03 | Enter multiple hosts | A separate result is shown for each non-empty host |
| T04 | Run repeated checks | New records are added to monitoring history |
| T05 | Download latest results | A CSV file containing latest results is downloaded |
| T06 | Download outage log | A CSV file containing recorded status transitions is downloaded |
| T07 | Enable auto-refresh with its dependency installed | Checks run on the configured 30-second refresh cycle while the app session is active |
| T08 | Clear history with confirmation enabled | Saved monitoring history and outage log are cleared |

Record the actual output from your own computer before marking a test as Pass.

---

## 14. Negative Testing

Negative testing verifies that the application handles invalid input and failure conditions without crashing or producing misleading results.

| Test ID | Test case | Steps / input | Expected behavior |
|---|---|---|---|
| N01 | Empty host list | Remove all host entries and click Run | The app displays a validation error and does not run checks |
| N02 | Invalid domain | Enter `this-domain-should-not-exist.invalid` and run HTTP or Ping | The check fails gracefully and displays diagnostic details; the app remains usable |
| N03 | Unresponsive destination | Try a reserved documentation IP such as `192.0.2.1` with Ping | A timeout or no-reply result is reported if the address does not respond from the test network |
| N04 | Non-existent page | Check `https://example.com/this-page-does-not-exist` using HTTP | If the server returns 404, the HTTP code is shown and the server is still considered reachable |
| N05 | Internet disconnected | Disconnect from Wi-Fi and run an HTTP check, then reconnect and check again | Failure is shown during disconnection; a later successful check can record recovery |
| N06 | Clear without confirmation | Leave the confirmation checkbox unticked and click Clear | A warning appears and the saved records remain intact |
| N07 | Ping unavailable | Run Ping on a system where the ping command is unavailable (only if safely testable) | The app reports that ping is unavailable instead of terminating |
| N08 | HTTP timeout or connection error | Use a host that does not respond or a controlled test endpoint with a short timeout | A connection error is displayed and other hosts can still be checked |

### Negative-testing notes

- A reserved IP address is intended for documentation and examples; behavior can vary with local routing and network configuration. Confirm the actual output rather than assuming a timeout.
- Some public servers block ping. Use HTTP mode to distinguish a ping restriction from a web-server response.
- Do not use a real third-party system to create disruption. Testing can be performed with invalid hostnames, reserved addresses, and your own connection.
- Mark each test **Pass** only after confirming the observed behavior. Add an **Actual Result** and **Pass/Fail** column to your test report.

---

## 15. Troubleshooting

### `streamlit` is not recognized
Activate the virtual environment and run:

```bash
python -m streamlit run app.py
```

### `requirements.txt` cannot be found
Make sure the terminal is open in the project directory containing both `app.py` and `requirements.txt`.

### Ping always fails
The target or network may block ICMP, or the ping command may be unavailable. Try **HTTP** or **Ping + HTTP** for a website. A failed ping alone does not prove that the website is down.

### HTTP checks fail
Check the hostname spelling, URL, internet connection, DNS configuration, proxy settings, certificate configuration, and whether the server accepts HTTP/HTTPS requests.

### No latency graph appears
The chart requires saved successful measurements with latency values. Run more checks and verify that at least one selected method is returning a measurement.

### Outage log is empty
The outage log is based on detected changes between recorded statuses. Run repeated checks and observe a status change. If a host has not changed status, there may be no event to display.

### Auto-refresh warning appears
Install the optional dependency:

```bash
pip install streamlit-autorefresh
```

Then restart Streamlit and enable auto-refresh again.

### Port 8501 is already in use
Start Streamlit on another port:

```bash
streamlit run app.py --server.port 8502
```

Then open `http://localhost:8502`.

---

## 16. Project Structure

```text
network_connectivity_monitor/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python package dependencies
├── README.md              # Project documentation
├── PBL_REPORT.md          # PBL report draft
├── .gitignore             # Optional Git ignore rules
└── data/                  # Created automatically when the app runs
    ├── monitor_history.csv
    └── outage_log.csv
```

The `data/` files are created automatically. They may not exist in a fresh copy until the application is launched.

---

## 17. Limitations

- This is an educational project, not a replacement for enterprise monitoring software.
- It checks hosts only when manually triggered or when optional auto-refresh runs; it is not a guaranteed always-on background service.
- Ping behavior and output formatting differ across operating systems.
- ICMP can be blocked by firewalls or target servers.
- Latency is an approximate measurement and can vary due to DNS, network congestion, routing, server load, and local system conditions.
- Packet loss is estimated from ping output and is not measured by HTTP checks.
- A host marked `UP` means at least one selected test succeeded; it does not guarantee that every service on that host is healthy.
- CSV history is stored on the local machine and can be lost if the files are deleted or the machine is damaged.
- Auto-refresh depends on the browser session and Streamlit app remaining active.

---

## 18. Future Enhancements

Possible improvements for future versions include:

- Email or desktop notifications when a monitored host goes down or recovers.
- User-defined monitoring intervals and thresholds.
- Exportable PDF reports and date-range filtering.
- Improved DNS lookup diagnostics and IPv4/IPv6 selection.
- A configurable list of monitored services and ports.
- A database backend for larger histories and multiple users.
- Unit tests and automated test coverage for parsing and status decisions.
- More robust per-host availability statistics and uptime percentage calculations.

These are potential enhancements, not features guaranteed to be included in the current version.

## 19. Conclusion

The Network Connectivity Monitor demonstrates basic Computer Networks concepts through a working Python application. It combines ping and HTTP checks with latency measurements, packet-loss estimates, status tracking, history visualization, and CSV-based logging. It also provides a practical way to perform positive and negative testing and to understand the limitations of connectivity checks.

The project is intended for learning and demonstration. Results should always be interpreted in context because a failed test can indicate a protocol restriction or local network issue rather than a completely offline destination.

---

## Responsible Use

Only monitor public hosts or systems you are authorized to test. Use reasonable check counts and timeouts. This application is intended for basic diagnostics and educational demonstrations, not for generating heavy traffic or disrupting services.
