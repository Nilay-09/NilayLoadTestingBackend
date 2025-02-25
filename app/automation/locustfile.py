from locust import User, task, between, events
from locust.exception import StopUser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from app.config.config import get_credentials,get_visual_labels,get_dashboard_url,get_filter_config
import time
import threading

# Global list to store per-user results
user_results = []


def measure_load_time(wait, label):
    start = time.time()
    wait.until(EC.presence_of_element_located(
        (By.XPATH, f"//div[normalize-space(@aria-label)='{label}']")))
    return time.time() - start



def measure_filter_apply_and_clear_time(wait, filter_label, filter_value):
    # Apply filter:
    filter_container = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//div[contains(@class, 'slicer-dropdown-menu') and @aria-label='{filter_label}']")
        )
    )
    dropdown_arrow = filter_container.find_element(By.TAG_NAME, "i")
    start = time.time()
    if filter_container.get_attribute("aria-expanded") != "true":
        dropdown_arrow.click()
    option = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//div[contains(@class, 'slicerItemContainer') and @title='{filter_value}']")
        )
    )
    option.click()
    wait.until(lambda d: option.get_attribute("aria-selected") == "true")
    apply_time = time.time() - start
    print(f"[User] Filter '{filter_label}: {filter_value}' applied in {apply_time:.2f} seconds")
    
    # Clear filter:
    filter_container = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//div[contains(@class, 'slicer-dropdown-menu') and @aria-label='{filter_label}']")
        )
    )
    dropdown_arrow = filter_container.find_element(By.TAG_NAME, "i")
    if filter_container.get_attribute("aria-expanded") != "true":
        dropdown_arrow.click()
    option = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//div[contains(@class, 'slicerItemContainer') and @title='{filter_value}']")
        )
    )
    option.click()
    wait.until(lambda d: option.get_attribute("aria-selected") != "true")
    print(f"[User] Filter '{filter_label}' cleared.")
    return apply_time

class SingleRunSeleniumUser(User):
    wait_time = between(1, 2)

    def on_start(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        self.email, self.password = get_credentials()
        self.dashboard_url = get_dashboard_url()
        self.has_run = False
        self.result = None
        print("[User] on_start completed.")

    @task(10)
    def run_once(self):
        if self.has_run:
            return
        self.has_run = True
        start_time = time.time()
        driver = self.driver
        wait = self.wait
        result = {}
        try:
            print("[User] Starting login process...")
            driver.get("https://app.powerbi.com")
            wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(self.email)
            wait.until(EC.element_to_be_clickable((By.ID, "submitBtn"))).click()
            wait.until(EC.visibility_of_element_located((By.ID, "i0118"))).send_keys(self.password)
            wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click()
            try:
                wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click()
            except Exception:
                pass
            wait.until(lambda d: "powerbi.com" in d.current_url)
            print("[User] Login successful.")

            print("[User] Loading dashboard...")
            print(self.dashboard_url)
            dash_start = time.time()
            driver.get(self.dashboard_url)
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]')
            ))
            dashboard_load_time = time.time() - dash_start
            print(f"[User] Dashboard loaded in {dashboard_load_time:.2f} seconds.")

            # Measure visuals concurrently
            print("[User] Measuring visual load times concurrently...")

            labels = get_visual_labels()
            if not labels:
                labels = ["Accuracy of Service Delivery", "Call Resolved/ Call UnResolved by Day"]
            visual_results = [None] * len(labels)
            def measure_visual(index, label):
                visual_results[index] = measure_load_time(wait, label)
            threads = []
            for i, label in enumerate(labels):
                t = threading.Thread(target=measure_visual, args=(i, label))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()
            visual_dict = dict(zip(labels, visual_results))
            print("[User] Visual load times:", visual_dict)

            # Measure each filter configuration sequentially
            print("[User] Measuring filter apply times for each filter configuration...")

            filter_configs = get_filter_config()
            if not filter_configs:
                filter_configs = [{"label": "Request Type", "value": "Special Request"}]
            filter_times = {}
            for fc in filter_configs:
                ft = measure_filter_apply_and_clear_time(wait, fc["label"], fc["value"])
                filter_times[fc["label"]] = ft
            print("[User] Filter times:", filter_times)

            total_time = time.time() - start_time
            result = {
                "dashboard_load_time": dashboard_load_time,
                "visual_load_times": visual_dict,
                "filter_apply_times": filter_times,
                "total_time": total_time,
                "error": None
            }
            self.result = result
            print(f"[User] Test completed in {total_time:.2f} seconds.")
            try:
                if hasattr(events, "request_success"):
                    events.request_success.fire(
                        request_type="selenium",
                        name="powerbi_test",
                        response_time=total_time * 1000,
                        response_length=0,
                    )
            except Exception as e:
                print("[User] Error firing request_success event:", e)
        except Exception as e:
            total_time = time.time() - start_time
            result = {
                "dashboard_load_time": None,
                "visual_load_times": {},
                "filter_apply_times": {},
                "total_time": total_time,
                "error": str(e)
            }
            self.result = result
            print("[User] Exception during test:", e)
            try:
                if hasattr(events, "request_failure"):
                    events.request_failure.fire(
                        request_type="selenium",
                        name="powerbi_test",
                        response_time=total_time * 1000,
                        response_length=0,
                        exception=e,
                    )
            except Exception:
                print("[User] events.request_failure not available")
        finally:
            self.driver.quit()
        if self.result is not None:
            from app.automation.locustfile import user_results
            user_results.append(self.result)
            print("[User] Result appended:", self.result)
        # End user execution (prevent further tasks)
        raise StopUser()

    
    @task(1)
    def idle(self):
        time.sleep(1)

    def on_stop(self):
        if self.driver:
            self.driver.quit()
