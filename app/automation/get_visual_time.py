import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def measure_load_time(wait, label, results, index):
    start_time = time.time()
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//div[normalize-space(@aria-label)='{label}']")))
        load_time = time.time() - start_time
        results[index] = load_time
    except Exception as ex:
        results[index] = None
        print(f"❌ Failed to find '{label}': {ex}")  
        
 
 
def measure_filter_apply_and_clear_time(wait, filter_label, filter_value):
    """
    Measures the time taken to apply a filter and then clear it by clicking the filter option again.
    
    Args:
        wait: Selenium WebDriverWait instance.
        filter_label (str): The aria-label of the filter dropdown (e.g., "Request Type").
        filter_value (str): The value to select/deselect (e.g., "Special Request").
    
    Returns:
        float: Time taken in seconds for the filter to apply.
    """
    # Locate the filter container using its class and aria-label.
    filter_container = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//div[contains(@class, 'slicer-dropdown-menu') and @aria-label='{filter_label}']")
        )
    )
    dropdown_arrow = filter_container.find_element(By.TAG_NAME, "i")
    
    # Start timer before applying the filter.
    start_time = time.time()
    
    # Open the dropdown if it's not already open.
    if filter_container.get_attribute("aria-expanded") != "true":
        dropdown_arrow.click()
    
    # Wait until the desired filter option is clickable and click it.
    option = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//div[contains(@class, 'slicerItemContainer') and @title='{filter_value}']")
        )
    )
    option.click()
    
    # Wait until the option indicates that the filter is applied.
    wait.until(lambda d: option.get_attribute("aria-selected") == "true")
    apply_time = time.time() - start_time
    print(f"Filter '{filter_label}: {filter_value}' applied in {apply_time:.2f} seconds")
    
    # --- Clear the Filter ---
    # Re-locate the filter container (to avoid stale element issues).
    filter_container = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//div[contains(@class, 'slicer-dropdown-menu') and @aria-label='{filter_label}']")
        )
    )
    dropdown_arrow = filter_container.find_element(By.TAG_NAME, "i")
    
    # Open the dropdown if not already open.
    if filter_container.get_attribute("aria-expanded") != "true":
        dropdown_arrow.click()
    
    # Re-locate the filter option and click it again to clear the filter.
    option = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//div[contains(@class, 'slicerItemContainer') and @title='{filter_value}']")
        )
    )
    option.click()
    
    # Wait until the option's "aria-selected" attribute is no longer "true" (filter cleared).
    wait.until(lambda d: option.get_attribute("aria-selected") != "true")
    print(f"Filter '{filter_label}' cleared.")
    
    return apply_time


