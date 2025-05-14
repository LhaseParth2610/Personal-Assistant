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

"""
When Selenium opens Gmail sometimes there might be some previously open compose windows (drafts), 
they remain open, which can interfere with the automation process

"""
def close_open_compose_windows(driver, wait):
    """Close any open compose windows in Gmail."""
    try:
        print("Checking for open compose windows...")
        # Locate all close buttons for open compose windows
        close_buttons = driver.find_elements(By.XPATH, "//img[@aria-label='Close']")
        
        for button in close_buttons:
            print("Closing an open compose window...")
            button.click()
            time.sleep(1)  # Small delay to ensure the window is closed
        print("All open compose windows have been closed.")
    except Exception as e:
        print(f"Error while closing compose windows: {e}")

def extract_recipient(prompt):
    """Extract email address from the prompt using regex."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, prompt)
    return match.group(0) if match else None

def generate_email_draft(prompt, recipient):
    """Generate subject and body using Mistral 7B, with recipient provided."""
    with Mistral(api_key=api_key) as client:
        
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
        
        # Attempt 1: More Robust Locator (Check aria-label in dev tools)
        print("Waiting for recipient field (Attempt 1: aria-label)...")
        recipient_locator = (By.CSS_SELECTOR, "textarea[aria-label='To recipients'], input[aria-label='To recipients']") # Try both textarea and input
        recipient_field = wait.until(EC.element_to_be_clickable(recipient_locator))
        print("Recipient field found using aria-label.")


        if recipient_field:
            print(f"Attempting to fill recipient: {recipient}")


        
            recipient_field.click() 
            time.sleep(0.5)
            recipient_field.send_keys(recipient)
            print("Filled recipient using click, sleep, send_keys.")
            
            print("Sending TAB key to confirm recipient and move focus...")
            recipient_field.send_keys(Keys.TAB)
            time.sleep(0.5) # giveing time so to adjust to the tab key being pressed

            
            # --- Fill Subject ---
            
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
    # Initialize Selenium driver
    driver = uc.Chrome(options=options, driver_executable_path=chrome_driver_path)
    wait = WebDriverWait(driver, 20)  # Adjust timeout as needed
    print("Navigating to Gmail...")
    driver.get("https://mail.google.com/mail/u/0/#inbox")
    close_open_compose_windows(driver,wait)

    print("Type 'exit' or 'break' to quit :D")
    while True:
        prompt = input("IdiotAid : How may I help you today? ")
        if prompt.lower() in ('break', 'exit'):
            break

        # Extract recipient from prompt
        recipient = extract_recipient(prompt)
        if not recipient:
            print("No valid email address found in prompt. Please include one.")
            continue

        # Generate initial email draft
        subject, body = generate_email_draft(prompt, recipient)
        """As the mistral7b model doesnt have contextual awareness updating the email drafte by just giving it the prompt of what to update was not possible so 
           here we are saving the current context and giving it to the model again for context. 
        """
        current_context = {
            "recipient": recipient,
            "subject": subject,
            "body": body
        }
        print(f"\nDraft:\nRecipient: {recipient}\nSubject: {subject}\nBody: {body}\n")

        # Fill Gmail draft
        fill_gmail_draft(driver, wait, recipient, subject, body)

        # Feedback loop
        while True:
            proceed = input("IdiotAid: Are you satisfied with this draft? Would you like to make any changes? (yes/no): ").strip().lower()
            if proceed == "yes":
                send_email(driver)
                break
            else:
                # Ask the user for changes

                new_prompt = input("IdiotAid: Please describe the changes you'd like to make to the draft: ").strip()
                
                # Creating a contextual promt that gives the model the current context as well as the new instructions for the update.
                contextual_prompt = f"""
                The current email draft is as follows:
                Subject: {current_context['subject']}
                Body: {current_context['body']}

                Please update the draft based on the following instructions:
                {new_prompt}
                """

                # Generate updated draft using Mistral
                updated_subject, updated_body = generate_email_draft(contextual_prompt, recipient)
                print(f"\nUpdated Draft:\nRecipient: {recipient}\nSubject: {updated_subject}\nBody: {updated_body}\n")

                # Update the Gmail draft
                update_gmail_draft(driver, updated_subject, updated_body)
                # after each update we are saving the context if need be for another update
                current_context["subject"]=updated_subject
                current_context["body"]=updated_body

                # Ask again if the user is satisfied
                continue  # Loop back to ask for feedback again

    # Clean up
    print("Quitting driver.")
    driver.quit()

if __name__ == "__main__":
    main()