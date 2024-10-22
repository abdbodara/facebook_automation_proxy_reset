import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
import time
from dotenv import load_dotenv
import os

load_dotenv()

# Load accounts from JSON
def load_accounts(filename='accounts.json'):
    with open(filename, 'r') as f:
        return json.load(f)

# Save results to JSON
def save_results(results, filename='successful_logins.json'):
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)

# Change IP using the proxy reset URL
def reset_proxy():
    reset_url = os.getenv('RESET_URL')
    try:
        response = requests.get(reset_url)

        if response.status_code == 200:
            print("IP reset successful!")
        else:
            print(f"IP Already reset!")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while trying to reset IP: {e}")

# Configure Selenium with proxy
def configure_driver_with_proxy(proxy_address):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    # options.add_argument("--incognito")

    # Set up the proxy
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = proxy_address
    proxy.ssl_proxy = proxy_address
    
    # Add proxy settings to Chrome options
    options.proxy = proxy
    
    # Path to your ChromeDriver (you can specify the path or use the default one)
    chrome_driver_path = os.getenv('DRIVER_PATH')  # Specify your chromedriver path

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Perform Facebook login
def facebook_login(driver, login_data):
    driver.get(os.getenv('FACEBOOK_PATH'))
    
    try:
        # Enter login credentials
        email_field = driver.find_element(By.ID, "email")
        email_field.send_keys(login_data['login'])
        
        password_field = driver.find_element(By.ID, "pass")
        password_field.send_keys(login_data['password'])
        password_field.send_keys(Keys.RETURN)
        
        # Wait for login to process (you may want to use WebDriverWait for better accuracy)
        time.sleep(5)

        # Check if login was successful by checking for user profile link or cookies
        if os.getenv('FACEBOOK_PATH') in driver.current_url:
            print(f"Login successful for {login_data['login']}")
            cookies = driver.get_cookies()
            return {"login": login_data['login'], "password": login_data['password'], "cookies": cookies}
        else:
            print(f"Login failed for {login_data['login']}")
            return {"login": login_data['login'], "password": login_data['password'], "status": "WRONG ACCOUNT"}
    
    except Exception as e:
        print(f"Error during login: {e}")
        return {"login": login_data['login'], "password": login_data['password'], "status": "WRONG ACCOUNT"}

def main():
    accounts = load_accounts()
    results = []

    for account in accounts:
        # Reset proxy before each login attempt
        reset_proxy()

        # Set up the proxy
        proxy_address = os.getenv("PROXY_ADDRESS")
        driver = configure_driver_with_proxy(proxy_address)

        # Try to log in
        result = facebook_login(driver, account)
        results.append(result)

        driver.quit()  # Close the browser after each attempt

    # Save results to the JSON file
    save_results(results)

if __name__ == "__main__":
    main()
