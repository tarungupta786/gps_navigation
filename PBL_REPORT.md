# PBL Project Report: Network Connectivity Monitor

## 1. Title
**Network Connectivity Monitor using Python**

## 2. Abstract
The Network Connectivity Monitor is a small application that checks whether selected hosts are reachable over a network. It supports ICMP ping checks, HTTP/HTTPS checks, and a combined mode. It displays host status, response latency, estimated ping packet loss, HTTP response codes, response-time history, and detected outage/recovery events. Monitoring records are saved locally as CSV files so they can be reviewed or downloaded.

## 3. Aim
To develop a simple application that monitors network connectivity and visualizes host availability and response performance.

## 4. Objectives
- Check the reachability of multiple hostnames, IP addresses, or URLs.
- Measure and display response time.
- Estimate packet loss using ping replies.
- Test web-server responses using HTTP/HTTPS.
- Maintain a history of checks and log outages/recoveries.
- Demonstrate basic Computer Networks concepts through a visual dashboard.

## 5. Software and Hardware Requirements
**Software:** Python 3.10+, Streamlit, Pandas, Requests, streamlit-autorefresh, a modern web browser.

**Hardware:** A regular laptop or desktop computer with network access. No special networking hardware is required.

## 6. Concepts Used
- Hostnames and IP addresses
- ICMP Echo Request and Echo Reply (ping)
- HTTP/HTTPS request-response communication
- Latency and packet loss
- Availability monitoring and troubleshooting
- Data logging and visualization

## 7. System Design / Working
1. The user enters one or more hosts in the sidebar.
2. The user selects Ping, HTTP, or Ping + HTTP.
3. The application performs the selected checks with a timeout.
4. It combines the results into an UP or DOWN status.
5. The dashboard displays latency, packet-loss estimate, and HTTP status where available.
6. Each check is stored in `data/monitor_history.csv`.
7. Changes from UP to DOWN and DOWN to UP are written to `data/outage_log.csv`.
8. The dashboard plots response-time history and offers CSV downloads.

## 8. Algorithm
1. Start the application.
2. Read host entries and monitoring settings.
3. For each host:
   - If Ping is enabled, send ping requests and calculate the available latency and packet-loss information.
   - If HTTP is enabled, issue an HTTP/HTTPS request and record the response code and request duration.
   - Mark the host UP if at least one selected check succeeds; otherwise mark it DOWN.
   - Compare the status with the previous saved status and log an outage or recovery transition if needed.
   - Save the result in the monitoring history.
4. Display the latest results, metrics, graph, and outage log.
5. Repeat when the user runs another check or enables auto-refresh.
6. Stop.

## 9. Testing Plan
| Test case | Action | Expected result |
|---|---|---|
| Valid reachable web host | Run HTTP check for a reachable website | HTTP response and response time are displayed |
| Host that replies to ping | Run Ping check | UP status and available latency/loss are displayed |
| Unreachable or invalid host | Run checks for a nonresponsive host | DOWN status or clear failure details are displayed |
| Multiple hosts | Enter several hosts on separate lines | Each host receives its own result row |
| Outage transition | Record a host as UP, then make it fail on a later check | Outage-start event is logged |
| Recovery transition | Record a host as DOWN, then check it successfully | Recovery event and estimated duration are logged |
| Export | Select a CSV download | A CSV file is downloaded |

## 10. Result
The application provides a dashboard for checking network reachability, observing response performance, and reviewing connectivity changes. Actual results depend on the computer's network, DNS, firewall rules, and the target host.

## 11. Limitations
- A ping failure does not always mean a host is down because ICMP may be blocked.
- HTTP checks apply to web services, not every type of host.
- The app records outages only when checks run; it is not a guaranteed 24/7 monitoring service.
- Packet loss is estimated from ping results only.

## 12. Future Enhancements
- Add email or desktop alerts for outages.
- Store data in SQLite or PostgreSQL for larger histories.
- Add configurable check intervals and host groups.
- Add exportable PDF reports and uptime summaries.
- Run a separate background monitoring service for continuous checks.

## 13. Conclusion
The Network Connectivity Monitor demonstrates core networking concepts using a practical Python application. It combines reachability checks, latency measurements, HTTP responses, and monitoring logs in a simple dashboard that can help with basic network troubleshooting.

## 14. Sample Viva Questions
1. What is the purpose of a network connectivity monitor?
2. What is ping, and which protocol does it commonly use?
3. What is the difference between an IP address and a hostname?
4. What is latency, and in which unit is it measured?
5. What does packet loss mean?
6. Why can a website be reachable over HTTP while ping fails?
7. What is the role of HTTP status codes?
8. Why does the application use timeouts?
9. What information is stored in the monitoring history?
10. What are the limitations of this project?
