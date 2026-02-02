#!/usr/bin/env python
"""Test script to verify servis_durumu form field behavior"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

# Setup
driver = webdriver.Chrome()
try:
    # Navigate to servis_durumu page
    driver.get("http://localhost:5000/servis_durumu")
    time.sleep(2)
    
    print("=" * 60)
    print("FORM FIELD TEST")
    print("=" * 60)
    
    # Find form elements
    statusSelect = driver.find_element(By.ID, "statusSelect")
    sistemSelect = driver.find_element(By.ID, "sistemSelect")
    altSistemSelect = driver.find_element(By.ID, "altSistemSelect")
    aciklamaInput = driver.find_element(By.ID, "aciklamaInput")
    
    print("\n1. INITIAL STATE:")
    print(f"   Sistem style: {sistemSelect.get_attribute('style')}")
    print(f"   Alt Sistem style: {altSistemSelect.get_attribute('style')}")
    print(f"   Açıklama style: {aciklamaInput.get_attribute('style')}")
    
    # Select "Servis Dışı" status
    print("\n2. SELECTING 'SERVIS DIŞI' STATUS...")
    status_options = statusSelect.find_elements(By.TAG_NAME, "option")
    for option in status_options:
        if "Servis Dışı" in option.text:
            print(f"   Found option: {option.text}")
            option.click()
            break
    
    time.sleep(1)
    
    print("\n3. AFTER SELECTING 'SERVIS DIŞI':")
    print(f"   Status selected value: {statusSelect.get_attribute('value')}")
    print(f"   Sistem style: {sistemSelect.get_attribute('style')}")
    print(f"   Alt Sistem style: {altSistemSelect.get_attribute('style')}")
    print(f"   Açıklama style: {aciklamaInput.get_attribute('style')}")
    
    # Try to check if element is clickable
    print(f"\n4. CLICKING SISTEM DROPDOWN:")
    try:
        sistemSelect.click()
        print("   ✓ Sistem dropdown clicked successfully!")
        
        # Wait for options to appear
        wait = WebDriverWait(driver, 3)
        options = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#sistemSelect option")))
        
        print(f"   Available options ({len(options)}):")
        for option in options[:3]:
            print(f"      - {option.text}")
        
        # Try to select first non-empty option
        for option in options:
            if option.text and option.text != "Seçiniz":
                print(f"\n   Selecting: {option.text}")
                option.click()
                time.sleep(1)
                break
        
        print("\n5. AFTER SELECTING SISTEM:")
        print(f"   Sistem value: {sistemSelect.get_attribute('value')}")
        print(f"   Alt Sistem style: {altSistemSelect.get_attribute('style')}")
        
        # Check alt sistem options
        alt_options = altSistemSelect.find_elements(By.TAG_NAME, "option")
        print(f"   Alt Sistem options: {len(alt_options)}")
        for option in alt_options[:3]:
            if option.text:
                print(f"      - {option.text}")
        
        print("\n✓ TEST COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"   ✗ ERROR clicking sistem: {e}")
        
finally:
    driver.quit()
