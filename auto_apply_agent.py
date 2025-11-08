# auto_apply_agent.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time
import traceback
import config

# ======================================
# DRIVER FACTORY
# ======================================
def create_driver(headless=False):
    """Create a Chrome WebDriver with best-practice options."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    return driver


# ======================================
# SAFE CLICK UTIL
# ======================================
def safe_click(driver, by, selector, timeout=8):
    """Wait until element clickable, then click."""
    try:
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, selector)))
        el.click()
        return True
    except Exception:
        return False


# ======================================
# LINKEDIN APPLY
# ======================================
def apply_linkedin(job_url, email=None, password=None, headless=False):
    """Automate LinkedIn Easy Apply jobs."""
    if not email or not password:
        print("⚠️ LinkedIn credentials not provided.")
        return False, "No credentials"

    driver = create_driver(headless=headless)
    try:
        print(f"🌐 Opening LinkedIn login page...")
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "username")))

        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)

        # check if captcha appeared
        if "checkpoint" in driver.current_url or "challenge" in driver.current_url:
            print("⚠️ CAPTCHA detected on LinkedIn login. Manual login required.")
            return False, "CAPTCHA login required"

        driver.get(job_url)
        time.sleep(3)

        print(f"🔎 Checking for Easy Apply button on: {job_url}")
        try:
            easy_apply = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Easy Apply') or contains(., 'Apply now')]"))
            )
            easy_apply.click()
            time.sleep(2)
        except Exception:
            return False, "Easy Apply not found"

        for _ in range(6):
            try:
                submit = driver.find_element(By.XPATH, "//button[contains(., 'Submit') or contains(., 'Done') or contains(., 'Apply')]")
                if submit.is_enabled():
                    submit.click()
                    time.sleep(3)
                    return True, "Submitted successfully"
            except NoSuchElementException:
                pass

            try:
                next_btn = driver.find_element(By.XPATH, "//button[contains(., 'Next') or contains(., 'Continue')]")
                next_btn.click()
                time.sleep(2)
            except Exception:
                break

        print("⚠️ Complex LinkedIn apply form detected (manual input required).")
        return False, "Complex flow (manual)"

    except Exception as e:
        print(f"⚠️ LinkedIn apply error: {e}")
        traceback.print_exc()
        return False, str(e)
    finally:
        driver.quit()


# ======================================
# INTERNSHALA APPLY
# ======================================
def apply_internshala(job_url, email=None, password=None, headless=False):
    """Automate Internshala apply."""
    if not email or not password:
        print("⚠️ Internshala credentials missing.")
        return False, "No credentials"

    driver = create_driver(headless=headless)
    try:
        driver.get("https://internshala.com/users/sign_in")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user_email")))

        driver.find_element(By.ID, "user_email").send_keys(email)
        driver.find_element(By.ID, "user_password").send_keys(password)
        driver.find_element(By.NAME, "commit").click()
        time.sleep(3)

        if "otp" in driver.current_url or "verify" in driver.current_url:
            print("⚠️ OTP verification required on Internshala.")
            return False, "OTP verification required"

        driver.get(job_url)
        time.sleep(3)

        print(f"🔎 Checking for Apply button on Internshala...")
        try:
            apply_btn = driver.find_element(By.XPATH, "//a[contains(@class,'apply_button') or contains(text(),'Apply Now') or contains(text(),'Apply')]")
            apply_btn.click()
            time.sleep(2)

            try:
                submit = driver.find_element(By.XPATH, "//input[@type='submit' or @value='Apply' or @value='Submit']")
                submit.click()
                time.sleep(2)
                return True, "Submitted successfully"
            except Exception:
                return True, "Apply clicked - manual finalize"
        except NoSuchElementException:
            return False, "Apply button not found"
    except Exception as e:
        print(f"⚠️ Internshala apply error: {e}")
        traceback.print_exc()
        return False, str(e)
    finally:
        driver.quit()


# ======================================
# WELLFOUND (ANGELLIST)
# ======================================
def apply_wellfound(job_url, email=None, password=None, headless=False):
    """Best-effort for Wellfound (AngelList)."""
    driver = create_driver(headless=headless)
    try:
        driver.get(job_url)
        time.sleep(2)

        print(f"🔎 Checking for Apply button on Wellfound...")
        if safe_click(driver, By.XPATH, "//button[contains(., 'Apply') or contains(., 'Apply now') or contains(., 'Quick Apply')]"):
            return True, "Clicked apply"
        return False, "No standard apply button found"
    except Exception as e:
        print(f"⚠️ Wellfound apply error: {e}")
        traceback.print_exc()
        return False, str(e)
    finally:
        driver.quit()


# ======================================
# JOBRIGHT APPLY
# ======================================
def apply_jobright(job_url, email=None, password=None, headless=False):
    """Basic Jobright apply automation."""
    driver = create_driver(headless=headless)
    try:
        driver.get(job_url)
        time.sleep(3)

        print(f"🔎 Checking for Apply link on Jobright...")
        try:
            apply_btn = driver.find_element(By.XPATH, "//a[contains(., 'Apply') or contains(., 'Apply now') or contains(., 'Apply on company site')]")
            apply_btn.click()
            time.sleep(3)
            return True, "Clicked apply"
        except NoSuchElementException:
            return False, "Apply button not found"
    except Exception as e:
        print(f"⚠️ Jobright apply error: {e}")
        traceback.print_exc()
        return False, str(e)
    finally:
        driver.quit()
