# Raspberry FC Mobile Price Tracker

## Project Overview
Raspberry FC Mobile Price Tracker is a tool using a Raspberry Pi server to monitor and track player market prices in mobile football games. This project aims to provide real-time price updates to gamers and data analysts, helping them make more informed buying and selling decisions.

## Features
- **Automatically retrieves the latest player price data.**
- **Provides price change notifications via email.**

## Technology Stack
- **Python**
- **Requests library** for API calls
- **SMTP protocol** for sending email notifications
- **Raspberry Pi** as the server

## Usage Guide

1. **Configure Player Data**:
   - Enter the full name, level, desired buy-low price, and sell-high price of players you are interested in `players_data.txt`. Project information for players will be provided in a list later.

2. **Set Up Email Notifications**:
   - In the `SendEmail()` function in `web_fc.py`, set the sender and receiver email addresses. This project example uses Google email.

3. **Schedule Price Checks**:
   - Use the `schedule` library to set the initial price check time with:
     ```python
     schedule.every().day.at("23:00").do(check_player_prices)
     ```
   - Subsequent running times will be adjusted dynamically based on the price update timings provided by Renderz.
## Raspberry Pi
1. **Systemd service**: at /etc/systemd/system/mycrawler.service
