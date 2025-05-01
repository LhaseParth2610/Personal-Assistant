import os
import re
from mistralai import Mistral
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains # Import ActionChains
import time

# Load environment variables
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

# Selenium setup
BRAVE_BINARY = "/usr/bin/brave"
chrome_driver_path = os.path.abspath("chromedriver")
PROFILE_DIR = os.path.expanduser("~/.config/BraveSoftware/Brave-Browser")

options = uc.ChromeOptions()
options.binary_location = BRAVE_BINARY
options.add_argument(f"--user-data-dir={PROFILE_DIR}")
options.add_argument("--profile-directory=Default")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")

# Initialize Selenium driver


def extract_recipient(prompt):
    """Extract email address from the prompt using regex."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, prompt)
    return match.group(0) if match else None

def generate_email_draft(prompt, recipient):
    """Generate subject and body using Mistral 7B, with recipient provided."""
    with Mistral(api_key=api_key) as client:
        # Structured prompt to infer subject and generate body
        mistral_prompt = f"""
        Based on the following prompt, infer an appropriate email subject and generate a professional email body. Return the result in the format:
        Subject: [subject line]
        Body: [email body]

        Prompt: {prompt}
        Note: The recipient's email is {recipient}. Do not include the recipient in the output.
        """
        resp = client.chat.complete(
            model="open-mistral-7b",
            messages=[{"role": "user", "content": mistral_prompt}]
        )
        response_text = resp.choices[0].message.content
        # Parse the response
        lines = response_text.split("\n")
        subject = body = ""
        for line in lines:
            if line.startswith("Subject:"):
                subject = line.replace("Subject:", "").strip()
            elif line.startswith("Body:"):
                body = line.replace("Body:", "").strip()
                # Capture multi-line body
                body += "\n".join([l for l in lines[lines.index(line)+1:] if l.strip()])
        return subject, body

def fill_gmail_draft(driver, wait, recipient, subject, body): # Pass driver and wait
    """Fill Gmail compose window with email draft."""
    print("Navigating to Gmail...")
    driver.get("https://mail.google.com/mail/u/0/#inbox")
    
    try:
        print("Waiting for Compose button...")
        compose_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Compose']"))
        )
        print("Clicking Compose button...")
        compose_button.click()
        # Add a small static wait AFTER clicking compose, as the popup needs time
        time.sleep(2) # Increased slightly

        # --- Try different locators and methods for the recipient field ---
        recipient_field = None
        try:
            # Attempt 1: More Robust Locator (Check aria-label in dev tools)
            print("Waiting for recipient field (Attempt 1: aria-label)...")
            recipient_locator = (By.CSS_SELECTOR, "textarea[aria-label='To recipients'], input[aria-label='To recipients']") # Try both textarea and input
            recipient_field = wait.until(EC.element_to_be_clickable(recipient_locator))
            print("Recipient field found using aria-label.")

        except TimeoutException:
            print("Recipient field with aria-label not found or clickable.")
            try:
                 # Attempt 2: Locator by name (Common for forms)
                print("Waiting for recipient field (Attempt 2: name='to')...")
                recipient_locator = (By.NAME, "to")
                recipient_field = wait.until(EC.element_to_be_clickable(recipient_locator))
                print("Recipient field found using name='to'.")
            except TimeoutException:
                 print("Recipient field with name='to' not found or clickable. Trying original ID (less recommended)...")
                 try:
                     # Attempt 3: Original ID (Fallback, less reliable)
                     recipient_locator = (By.ID, "uu") # Your original locator
                     recipient_field = wait.until(EC.element_to_be_clickable(recipient_locator))
                     print("Recipient field found using ID='uu'.")
                 except TimeoutException:
                     print("ERROR: Could not find or click the recipient field using multiple strategies.")
                     return # Exit function if field cannot be found

        # ... inside fill_gmail_draft, after finding recipient_field ...

        if recipient_field:
            print(f"Attempting to fill recipient: {recipient}")

            # Method 1: Click, Pause, Send Keys (if this worked)
            try:
                recipient_field.click() # Ensure focus
                time.sleep(0.5)
                recipient_field.send_keys(recipient)
                print("Filled recipient using click, sleep, send_keys.")
                # ****** ADD THIS LINE ******
                print("Sending TAB key to confirm recipient and move focus...")
                recipient_field.send_keys(Keys.TAB)
                time.sleep(0.5) # Brief pause for UI to react to TAB
                # **************************

                # Now proceed to Subject field without extra clicks here

            except Exception as e:
                print(f"Method 1 failed: {e}. Trying Method 2 (JavaScript)...")
                # Method 2: JavaScript Execution (if this worked)
                try:
                    driver.execute_script("arguments[0].value = arguments[1];", recipient_field, recipient)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", recipient_field)
                    print("Filled recipient using JavaScript.")
                    # ****** ADD THIS LINE ******
                    print("Sending TAB key to confirm recipient and move focus...")
                    recipient_field.send_keys(Keys.TAB)
                    time.sleep(0.5) # Brief pause for UI to react to TAB
                    # **************************

                     # Now proceed to Subject field without extra clicks here

                except Exception as js_e:
                     print(f"ERROR: JavaScript method failed: {js_e}")
                     return

            # --- Fill Subject ---
            # Wait specifically for the subject field to be ready AFTER sending TAB
            print("Waiting for Subject field...")
            subject_field = wait.until(EC.visibility_of_element_located((By.NAME, "subjectbox")))
            print("Filling subject...")
            subject_field.send_keys(subject) # Should have focus now, but sending keys targets it anyway

            # --- Fill Body ---
            print("Waiting for Body field...")
            body_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[aria-label='Message Body']")))
            print("Filling body...")
            body_field.send_keys(body)
            print("Draft filled.")

        else:
            print("ERROR: Could not proceed without locating the recipient field.")

# ... rest of the code ...
    except TimeoutException as e:
        print(f"Error during Gmail interaction (Timeout): {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def update_gmail_draft(driver,subject, body):
    """Update the existing Gmail draft with new subject and body."""
    # Clear and update subject
    subject_field = driver.find_element(By.NAME, "subjectbox")
    subject_field.clear()
    subject_field.send_keys(subject)

    # Clear and update body
    body_field = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Message Body']")
    body_field.clear()
    body_field.send_keys(body)

def send_email(driver):
    """Send the email using Selenium."""
    send_button = driver.find_element(By.XPATH, "//div[text()='Send']")
    send_button.click()
    print("Email sent!")

def main():
    # ...(your existing setup)...
    # Initialize Selenium driver (ensure driver and wait are defined)
    driver = uc.Chrome(options=options, driver_executable_path=chrome_driver_path)
    wait = WebDriverWait(driver, 20) # Adjust timeout as needed

    print("Type 'exit' or 'break' to quit :D")
    while True:
        prompt = input("Enter your email prompt (include recipient email): ")
        if prompt.lower() in ('break', 'exit'):
            break

        # Extract recipient from prompt
        recipient = extract_recipient(prompt)
        if not recipient:
            print("No valid email address found in prompt. Please include one.")
            continue

        # Generate initial email draft
        subject, body = generate_email_draft(prompt, recipient)
        print(f"\nDraft:\nRecipient: {recipient}\nSubject: {subject}\nBody: {body}\n")

        # Fill Gmail draft - pass driver and wait
        fill_gmail_draft(driver, wait, recipient, subject, body)

        # Feedback loop
        # ... (rest of your feedback loop - ensure driver/wait are available if needed) ...
        # Make sure update_gmail_draft also uses robust waits/locators if needed

    # Clean up
    print("Quitting driver.")
    driver.quit()


if __name__ == "__main__":
    main()