import os
import time
from time import sleep
from random import uniform, random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- KONFIGURATION (Secrets aus ENV) ---
USERNAME = os.environ["SJ_USERNAME"]
PASSWORD = os.environ["SJ_PASSWORD"]
VOTE_LIMIT = 500

# --- Headless Chrome für GitHub Actions ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

# --- Zeitmessung & Status ---
start_time = time.time()
vote_count = 0
points = 0
processed_ids = set()

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def format_duration(seconds):
    mins, secs = divmod(int(seconds), 60)
    return f"{mins}m {secs}s"

def wait_click(by, identifier):
    try:
        elem = wait.until(EC.element_to_be_clickable((by, identifier)))
        elem.click()
        return True
    except Exception as e:
        log(f"❌ Fehler bei Klick auf {identifier}: {e}")
        return False

def login():
    driver.get("http://www.secretgermanjodel.com")
    sleep(1)
    wait_click(By.CLASS_NAME, "alertButtonGreen")
    driver.find_element(By.NAME, "sj_username").send_keys(USERNAME)
    sleep(0.3)
    driver.find_element(By.NAME, "sj_password").send_keys(PASSWORD)
    wait_click(By.CLASS_NAME, "alertButtonGreen")
    sleep(1)

def get_points():
    try:
        badge = driver.find_element(By.ID, "hoehepunkteBadge")
        raw_text = badge.text.replace(" ", "").strip()
        return int(raw_text)
    except Exception as e:
        log(f"❌ Fehler beim Lesen des Punktestands: {e}")
        return None

def vote_loop():
    global vote_count
    start_points = get_points()
    if start_points is None:
        log("🔴 Initialer Punktestand konnte nicht gelesen werden. Abbruch.")
        return

    target_increase = 1002
    target_points = start_points + target_increase
    log(f"🎯 Starte Voting bei {start_points} Punkten, Ziel: {target_points} Punkte (+{target_increase})")

    unchanged_counter = 0
    unchanged_threshold = 20

    while True:
        current_points = get_points()
        if current_points is None:
            continue

        if current_points >= target_points:
            elapsed = time.time() - start_time
            log(f"🎉 Ziel erreicht: {current_points} Punkte nach {vote_count} Votes!")
            log(f"⏱ Gesamtdauer: {format_duration(elapsed)}")
            return

        jodels = driver.find_elements(By.XPATH, "//*[@jodel-id]")
        for jodel in jodels:
            jodel_id = jodel.get_attribute("jodel-id")
            if jodel_id in processed_ids:
                continue
            processed_ids.add(jodel_id)

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", jodel)
            sleep(uniform(0.2, 0.35))

            try:
                action = "up" if random() < 0.8 else "down"
                vote_btn = jodel.find_element(By.XPATH, f".//div[contains(@class, 'e-el-votes-{action}')]")

                before = get_points()
                if before is None:
                    continue

                driver.execute_script("arguments[0].click();", vote_btn)
                sleep(uniform(0.6, 0.9))

                after = get_points()
                if after is None:
                    continue

                if after > before:
                    vote_count += 1
                    unchanged_counter = 0
                    log(f"✔ Erfolgreicher {action}-Vote für Jodel-ID {jodel_id} | Punkte: {after}")

                    if vote_count % 5 == 0:
                        elapsed = time.time() - start_time
                        log(f"*** {vote_count} Votes | {after} Punkte | Elapsed: {format_duration(elapsed)} ***")
                else:
                    unchanged_counter += 1
                    log(f"⚠️ Vote ohne Zählung ({unchanged_counter}/{unchanged_threshold})")
                    if unchanged_counter >= unchanged_threshold:
                        elapsed = time.time() - start_time
                        log(f"🛑 Voting-Limit erreicht. Abbruch bei {after} Punkten.")
                        log(f"⏱ Gesamtdauer: {format_duration(elapsed)}")
                        return

            except Exception as e:
                log(f"❌ Fehler bei Vote für Jodel-ID {jodel_id}: {e}")

        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        sleep(uniform(0.4, 0.6))

# --- AUSFÜHRUNG ---
try:
    login()
    vote_loop()
except KeyboardInterrupt:
    log("🔴 Manuell abgebrochen.")
finally:
    elapsed = time.time() - start_time
    log(f"✅ FERTIG: {points} Punkte aus {vote_count} Votes")
    log(f"⏱ Gesamtdauer: {format_duration(elapsed)}")
    driver.quit()
