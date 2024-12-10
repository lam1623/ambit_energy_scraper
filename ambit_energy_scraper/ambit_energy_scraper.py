#!/usr/bin/env python3
# Version: v24.0
# Description:
# - Logs into Ambit Energy, navigates to My Bill and Usage History.
# - Extracts data organized by years, months, weeks, days, and 15-minute intervals.
# - Dynamically handles "Show 6 More" to load all available data.
# - Sends new data to Home Assistant via REST API.
# - Saves state to continue from the last extraction in future runs.

import logging
import json
import datetime
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Load configurations from environment variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")

# State and Data Files
STATE_FILE = "ambit_energy_last_state.json"
DATA_FILE = "ambit_energy_usage.json"

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


def wait_page_load_complete(driver, timeout=30):
    """Waits for the page to fully load."""
    logging.info("Waiting for page to load completely (readyState=complete)...")
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    logging.info("Page loaded completely.")


def click_show_more(driver):
    """
    Clicks all available 'Show 6 More' buttons until none remain.
    """
    while True:
        try:
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-usage="showSixMore"]'))
            )
            if show_more_button.is_displayed():
                logging.info("Clicking 'Show 6 More'...")
                show_more_button.click()
                wait_page_load_complete(driver)
            else:
                logging.info("No more 'Show 6 More' buttons found.")
                break
        except Exception:
            logging.info("No more 'Show 6 More' buttons found.")
            break


def login(driver, username, password):
    """Logs into the Ambit Energy website."""
    logging.info("Navigating to the login page...")
    driver.get(LOGIN_URL)
    logging.info("Waiting for the username field...")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "login-username")))

    logging.info("Entering credentials...")
    driver.find_element(By.ID, "login-username").send_keys(username)
    driver.find_element(By.ID, "login-password").send_keys(password)
    logging.info("Clicking 'Sign In'...")
    driver.find_element(By.ID, "login-submit").click()
    wait_page_load_complete(driver)


def navigate_to_my_bill(driver):
    """Navigates to the 'My Bill' section."""
    logging.info("Waiting for 'My Bill' link...")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'ul#nav a[href="/my-bill"]'))
    )
    my_bill_link = driver.find_element(By.CSS_SELECTOR, 'ul#nav a[href="/my-bill"]')
    logging.info("Clicking on 'My Bill'...")
    my_bill_link.click()
    wait_page_load_complete(driver)

    # Click 'Show 6 More' if present to load all months
    click_show_more(driver)

    logging.info("Waiting for 'Usage History' link...")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Usage History"))
    )
    logging.info("'My Bill' section loaded.")


def navigate_to_usage_history(driver):
    """Navigates to the 'Usage History' section."""
    logging.info("Locating 'Usage History' link...")
    usage_history_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Usage History")
    logging.info("Clicking on 'Usage History'...")
    usage_history_link.click()
    wait_page_load_complete(driver)

    # Click 'Show 6 More' if present to load all weeks
    click_show_more(driver)

    logging.info("Waiting for 'yearly-usage' section...")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "yearly-usage"))
    )
    logging.info("'Usage History' section loaded.")


def get_year(dt_str):
    """Extracts the year from an ISO-formatted date string."""
    return datetime.datetime.fromisoformat(dt_str.replace("Z", "")).year


def get_month(dt_str):
    """Extracts the month from an ISO-formatted date string."""
    return datetime.datetime.fromisoformat(dt_str.replace("Z", "")).month


def parse_yearly_data(driver):
    """Extracts monthly data from the annual view."""
    logging.info("Extracting yearly data (months)...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    yearly_box = soup.find("div", id="yearly-usage")
    months_data = []

    if yearly_box:
        usage_right = yearly_box.find("div", class_="usage-right")
        if usage_right:
            month_links = usage_right.find_all("a", class_="bar-a", attrs={"data-usage": "selectMonth"})
            for m in month_links:
                minfo = {
                    "start_date": m.get("data-start-date"),
                    "end_date": m.get("data-end-date"),
                    "month_total_kwh": None
                }
                t_usage = m.get("data-total-usage")
                if t_usage:
                    try:
                        minfo["month_total_kwh"] = float(t_usage)
                    except:
                        minfo["month_total_kwh"] = None
                months_data.append(minfo)
    logging.info(f"Extracted months: {months_data}")
    return months_data


def parse_monthly_data(driver):
    """Extracts weekly data from the monthly view."""
    logging.info("Extracting monthly data (weeks)...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    monthly_box = soup.find("div", id="monthly-usage")
    weeks_data = []

    if monthly_box:
        usage_right = monthly_box.find("div", class_="usage-right")
        if usage_right:
            week_links = usage_right.find_all("a", class_="bar-a", attrs={"data-usage": "selectWeek"})
            for w in week_links:
                winfo = {
                    "start_date": w.get("data-start-date"),
                    "end_date": w.get("data-end-date"),
                    "week_total_kwh": None
                }
                wu = w.get("data-total-usage")
                if wu:
                    try:
                        winfo["week_total_kwh"] = float(wu)
                    except:
                        winfo["week_total_kwh"] = None
                weeks_data.append(winfo)
    logging.info(f"Extracted weeks: {weeks_data}")
    return weeks_data


def parse_weekly_data(driver):
    """Extracts daily data from the weekly view."""
    logging.info("Extracting weekly data (days)...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    weekly_box = soup.find("div", id="weekly-usage")
    days_data = []

    if weekly_box:
        usage_right = weekly_box.find("div", class_="usage-right")
        if usage_right:
            day_links = usage_right.find_all("a", class_="bar-a", attrs={"data-usage": "selectDay"})
            for d in day_links:
                dinfo = {
                    "date": d.get("data-date"),
                    "day_total_kwh": None
                }
                du = d.get("data-total-usage")
                if du:
                    try:
                        dinfo["day_total_kwh"] = float(du)
                    except:
                        dinfo["day_total_kwh"] = None
                days_data.append(dinfo)
    logging.info(f"Extracted days: {days_data}")
    return days_data


def parse_daily_data(driver):
    """Extracts 15-minute interval data from the daily view."""
    logging.info("Extracting daily data (15-minute intervals)...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    daily_box = soup.find("div", id="daily-usage")
    intervals = []

    if daily_box:
        intervals_container = daily_box.find("div", id="interval-usage")
        if intervals_container:
            hour_divs = intervals_container.find_all("div", class_="hour")
            for hour_div in hour_divs:
                spans = hour_div.find_all("span", class_="bar-span")
                for sp in spans:
                    title = sp.get("title")
                    if title:
                        parts = title.split(",")
                        if len(parts) == 2:
                            time_str = parts[0].strip()
                            usage_str = parts[1].strip().replace(" kWh", "")
                            try:
                                usage_val = float(usage_str)
                            except:
                                usage_val = None
                            intervals.append({"time": time_str, "kwh": usage_val})
    logging.info(f"Extracted intervals: {intervals}")
    return intervals


def click_element(driver, by, value, description):
    """Generic function to wait for and click an element."""
    logging.info(f"Looking for element to {description}...")
    try:
        element = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((by, value))
        )
        logging.info(f"Clicking to {description}...")
        element.click()
    except Exception as e:
        logging.error(f"Could not click to {description}: {e}")
        logging.error("Current HTML content for diagnosis:")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        logging.error(soup.prettify())
        raise e
    wait_page_load_complete(driver)


def parse_structure(driver):
    """Extracts the complete data structure organized by years, months, weeks, days, and intervals."""
    data = {"years": {}}

    # Extract all months
    months = parse_yearly_data(driver)
    for month_info in months:
        year_str = str(get_year(month_info["start_date"]))
        month_str = str(get_month(month_info["start_date"]))

        if year_str not in data["years"]:
            data["years"][year_str] = {"months": {}}

        if month_str not in data["years"][year_str]["months"]:
            data["years"][year_str]["months"][month_str] = {
                "start_date": month_info["start_date"],
                "end_date": month_info["end_date"],
                "weeks": []
            }

        # Click on the month
        month_selector = f'a.bar-a[data-start-date="{month_info["start_date"]}"]'
        try:
            click_element(driver, By.CSS_SELECTOR, month_selector, f"month {month_info['start_date']}")
        except:
            logging.error(f"Could not click on month {month_info['start_date']}. Continuing to next month.")
            continue

        # Click 'Show 6 More' to load all weeks
        click_show_more(driver)

        # Extract weeks
        weeks = parse_monthly_data(driver)
        if not weeks:
            logging.warning(f"No weeks found for month {month_info['start_date']}.")
            continue

        for week_info in weeks:
            week_obj = {
                "start_date": week_info["start_date"],
                "end_date": week_info["end_date"],
                "days": {}
            }

            # Click on the week
            week_selector = f'a.bar-a[data-start-date="{week_info["start_date"]}"]'
            try:
                click_element(driver, By.CSS_SELECTOR, week_selector, f"week {week_info['start_date']}")
            except:
                logging.error(f"Could not click on week {week_info['start_date']}. Continuing to next week.")
                continue

            # Click 'Show 6 More' to load all days
            click_show_more(driver)

            # Extract days
            days = parse_weekly_data(driver)
            if not days:
                logging.warning(f"No days found for week {week_info['start_date']}.")
                continue

            for day_info in days:
                # Click on the day
                day_selector = f'a.bar-a[data-date="{day_info["date"]}"]'
                try:
                    click_element(driver, By.CSS_SELECTOR, day_selector, f"day {day_info['date']}")
                except:
                    logging.error(f"Could not click on day {day_info['date']}. Continuing to next day.")
                    continue

                # Extract intervals
                intervals = parse_daily_data(driver)
                week_obj["days"][day_info["date"]] = {
                    "day_total_kwh": day_info["day_total_kwh"],
                    "intervals": intervals
                }

            data["years"][year_str]["months"][month_str]["weeks"].append(week_obj)

    return data


def load_state():
    """Loads the last sent state from the state file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        logging.info(f"Loaded state: {state}")
        return state
    else:
        logging.info("No state file found. Starting fresh.")
        return {"last_sent": None}


def save_state(state):
    """Saves the current state to the state file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
    logging.info(f"Saved state: {state}")


def load_existing_data():
    """Loads existing data to prevent duplicates."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        logging.info("Loaded existing data.")
        return data
    else:
        logging.info("No existing data file found. Creating a new one.")
        return {"years": {}}


def save_data(data):
    """Saves the extracted data to the data file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    logging.info("Saved data to JSON file.")


def find_new_data(existing_data, new_data):
    """Finds new data that hasn't been sent to Home Assistant yet."""
    last_sent = existing_data.get("last_sent")
    logging.info(f"Last sent data: {last_sent}")

    to_send = []
    for year, ydata in new_data["years"].items():
        for month, mdata in ydata["months"].items():
            for week in mdata["weeks"]:
                for day_date, day_info in week["days"].items():
                    if last_sent:
                        day_datetime = datetime.datetime.fromisoformat(day_date.replace("Z", ""))
                        last_sent_datetime = datetime.datetime.fromisoformat(last_sent.replace("Z", ""))
                        if day_datetime <= last_sent_datetime:
                            continue
                    to_send.append({
                        "year": year,
                        "month": month,
                        "week_start_date": week["start_date"],
                        "week_end_date": week["end_date"],
                        "day_date": day_date,
                        "day_total_kwh": day_info["day_total_kwh"],
                        "intervals": day_info["intervals"]
                    })

    logging.info(f"New data to send: {len(to_send)} records.")
    return to_send


def send_data_to_home_assistant(data):
    """Sends data to Home Assistant via REST API."""
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }

    # Construct the payload
    payload = {
        "state": data["day_total_kwh"],
        "attributes": {
            "year": data["year"],
            "month": data["month"],
            "week_start_date": data["week_start_date"],
            "week_end_date": data["week_end_date"],
            "day_date": data["day_date"],
            "intervals": data["intervals"]
        }
    }

    response = requests.post(HA_URL, headers=headers, json=payload)
    if response.status_code == 200:
        logging.info(f"Sent data to Home Assistant for day {data['day_date']}.")
        return True
    else:
        logging.error(f"Failed to send data to Home Assistant: {response.status_code} - {response.text}")
        return False


def main():
    logging.info("Starting Selenium v24.0 for complete data extraction...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        # Login
        login(driver, USERNAME, PASSWORD)

        # Navigate to My Bill
        navigate_to_my_bill(driver)

        # Navigate to Usage History
        navigate_to_usage_history(driver)

        # Extract the entire data structure
        new_data = parse_structure(driver)

        # Load state and existing data
        state = load_state()
        existing_data = load_existing_data()

        # Find new data to send
        to_send = find_new_data(state, new_data)

        # Send data to Home Assistant and update state
        for data in to_send:
            success = send_data_to_home_assistant(data)
            if success:
                # Update the last sent date
                state["last_sent"] = data["day_date"]
                save_state(state)

        # Save the new data
        save_data(new_data)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()

