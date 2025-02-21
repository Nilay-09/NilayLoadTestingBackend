import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from get_visual_time import measure_load_time,measure_filter_apply_and_clear_time

import threading
import traceback

# --- Parameters ---
email = "priyank@innovationalofficesolution.com"
password = "MagicGriD@9876"

dashboard_url = (
    "https://app.powerbi.com/reportEmbed?reportId=72864037-20c2-4704-a490-f0d4502ec34c"
    "&autoAuth=true&ctid=99fa199d-2653-4e16-bd65-17cc244b425e"
)



# aria-label="Accuracy of Service Delivery "
# --- Initialize WebDriver ---
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start browser maximized
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)  # 20 seconds timeout




        
        
try:
    # Start time tracking
    start_time = time.time()

    # Open Power BI login page
    driver.get("https://app.powerbi.com")

    # Wait for the email input field and enter email
    email_field = wait.until(EC.visibility_of_element_located((By.ID, "email")))
    email_field.clear()
    email_field.send_keys(email)

    # Click the "Next" button
    next_button = wait.until(EC.element_to_be_clickable((By.ID, "submitBtn")))
    next_button.click()

    # Wait for the password field and enter password
    password_field = wait.until(EC.visibility_of_element_located((By.ID, "i0118")))
    password_field.clear()
    password_field.send_keys(password)

    # Click the "Sign In" button
    sign_in_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    sign_in_button.click()

    # Handle the "Stay Signed In" prompt if it appears
    try:
        stay_signed_in = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        stay_signed_in.click()
    except:
        print("Stay signed in prompt not displayed. Continuing...")

    # Wait for successful login by checking URL change
    wait.until(lambda driver: "powerbi.com" in driver.current_url)

    # Navigate to the dashboard URL
    driver.get(dashboard_url)

    # Wait for the dashboard container to load
    dashboard_start_time = time.time()
    dashboard_element = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]')
    ))
    dashboard_end_time = time.time()

    # Calculate load time
    dashboard_load_time = round(dashboard_end_time - dashboard_start_time, 2)
    total_time_taken = round(dashboard_end_time - start_time, 2)
    

    print(f"✅ Dashboard loaded successfully!")
    print(f"⏳ Time taken to load the dashboard after navigation: {dashboard_load_time} seconds")
    print(f"⏱️ Total time taken from login to dashboard load: {total_time_taken} seconds")
    

    
        

    
    
    
    
    
    
    
    labels = ["Accuracy of Service Delivery", "Call Resolved/ Call UnResolved by Day"]

    # Shared list for storing load times
    results = [None] * len(labels)
    threads = []

    # Create and start a thread for each label
    for i, lbl in enumerate(labels):
        t = threading.Thread(target=measure_load_time, args=(wait, lbl, results, i))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Print the results
    for i, lbl in enumerate(labels):
        if results[i] is not None:
            print(f"🔹 {lbl} loaded in {results[i]:.2f} seconds")
        else:
            print(f"🔹 {lbl} not found")


    try:
        measure_filter_apply_and_clear_time(wait, "Request Type", "Special Request")
        
    except Exception as e:
        print("❌ An error occurred:", e)
        traceback.print_exc()

except Exception as e:
    print("❌ An error occurred:", e)
    sys.exit(1)
finally:
    driver.quit()
