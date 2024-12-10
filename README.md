# Ambit Energy Scraper Add-on for Home Assistant

![Logo](https://path-to-your-logo.png)

## Overview

The **Ambit Energy Scraper** is a custom Home Assistant Add-on designed to automate the extraction of energy consumption data from the [Ambit Energy](https://www.ambitenergy.com/) portal. It organizes the data hierarchically by year, month, week, day, and 15-minute intervals, sending the information directly to Home Assistant for real-time monitoring and visualization.

## Features

- **Automated Login**: Securely logs into your Ambit Energy account.
- **Data Extraction**: Scrapes energy usage data organized by year, month, week, day, and 15-minute intervals.
- **State Management**: Maintains state to ensure only new data is sent to Home Assistant.
- **Home Assistant Integration**: Sends data via Home Assistant's REST API, updating a custom sensor.
- **Scheduling**: Automatically runs at scheduled intervals (e.g., every 6 hours).
- **Logging**: Provides detailed logs for monitoring and troubleshooting.

## Prerequisites

- **Home Assistant**: Ensure you have Home Assistant installed and running.
- **Selenium WebDriver**: The add-on uses Selenium for web automation.
- **Chromium & Chromedriver**: Required for Selenium to interact with the web browser.
- **Python 3.10 or Higher**: The script is built using Python 3.10.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ambit_energy_scraper.git

