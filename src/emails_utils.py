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
import time
import threading

# Load environment variables
load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")


class EmailAssistant:
    def __init__(self, display_callback, input_callback):
        self.display_callback = display_callback
        self.input_callback = input_callback
        self.driver = None
        self.wait = None
        self.selenium_initialized = False
        self.feedback_active = False  # Flag to track feedback loop

    def set_feedback_active(self, state):
        """Set feedback loop active state."""
        self.feedback_active = state

    def setup_selenium(self):
        """Set up Selenium with Brave browser."""
        if self.selenium_initialized:
            return

        BRAVE_BINARY = "/usr/bin/brave"
        chrome_driver_path = os.path.abspath("chromedriver")
        PROFILE_DIR = os.path.expanduser("~/.config/BraveSoftware/Brave-Browser")

        options = uc.ChromeOptions()
        options.binary_location = BRAVE_BINARY
        options.add_argument(f"--user-data-dir={PROFILE_DIR}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")

        self.driver = uc.Chrome(options=options, driver_executable_path=chrome_driver_path)
        self.wait = WebDriverWait(self.driver, 20)
        self.selenium_initialized = True

    
    # def close_open_compose_windows(self):
        
    #     try:
    #         print("Checking for open compose windows...")
    #         # Locate all close buttons for open compose windows
    #         close_buttons = self.driver.find_elements(By.XPATH, "//img[@aria-label='Save & close']")
    #         for button in close_buttons:
    #             print("Closing an open compose window...")
    #             button.click()
    #             time.sleep(1)  # Small delay to ensure the window is closed
    #         print("All open compose windows have been closed.")
    #     except Exception as e:
    #         print(f"Error while closing compose windows: {e}")
    
    def close_open_compose_windows(self, max_retries=3, delay=2):
        """Close any open compose windows in Gmail with retries."""
        try:
            for _ in range(max_retries):
                # Wait for Gmail to load and check for open compose windows
                close_buttons = self.driver.find_elements(By.XPATH, "//img[@aria-label='Save & close']")
                if close_buttons:
                    for button in close_buttons:
                        button.click()
                        time.sleep(1)  # Small delay between closing windows
                    return  # Exit after successfully closing all windows
                else:
                    # If no close buttons are found, wait and retry
                    time.sleep(delay)
            self.display_callback("No open compose windows found or unable to close them.")
        except Exception as e:
            self.display_callback(f"Error while closing compose windows: {e}")

    def extract_recipient(self, prompt):
        """Extract email address from the prompt using regex."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, prompt)
        return match.group(0) if match else None

    def generate_email_draft(self, prompt, recipient):
        """Generate subject and body using Mistral 7B."""
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
            lines = response_text.split("\n")
            subject = body = ""
            for line in lines:
                if line.startswith("Subject:"):
                    subject = line.replace("Subject:", "").strip()
                elif line.startswith("Body:"):
                    body = line.replace("Body:", "").strip()
                    body += "\n".join([l for l in lines[lines.index(line)+1:] if l.strip()])
            return subject, body

    def fill_gmail_draft(self, recipient, subject, body):
        """Fill Gmail compose window with email draft."""
        self.driver.get("https://mail.google.com/mail/u/0/#inbox")
        try:
            compose_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[text()='Compose']"))
            )
            compose_button.click()
            time.sleep(2)

            recipient_field = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[aria-label='To recipients'], input[aria-label='To recipients']"))
            )
            recipient_field.click()
            time.sleep(0.5)
            recipient_field.send_keys(recipient)
            recipient_field.send_keys(Keys.TAB)
            time.sleep(0.5)

            subject_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "subjectbox")))
            subject_field.send_keys(subject)

            body_field = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[aria-label='Message Body']")))
            body_field.send_keys(body)

        except TimeoutException:
            self.display_callback("Error: Timed out while interacting with Gmail.")
            return False
        except Exception as e:
            self.display_callback(f"An unexpected error occurred: {e}")
            return False
        return True

    def update_gmail_draft(self, subject, body):
        """Update the existing Gmail draft with new subject and body."""
        try:
            subject_field = self.driver.find_element(By.NAME, "subjectbox")
            subject_field.clear()
            subject_field.send_keys(subject)

            body_field = self.driver.find_element(By.CSS_SELECTOR, "div[aria-label='Message Body']")
            body_field.clear()
            body_field.send_keys(body)
        except Exception as e:
            self.display_callback(f"Error updating draft: {e}")
            return False
        return True

    def send_email(self):
        """Send the email using Selenium."""
        try:
            send_button = self.driver.find_element(By.XPATH, "//div[text()='Send']")
            send_button.click()
            self.display_callback("Email sent successfully!")
        except Exception as e:
            self.display_callback(f"Error sending email: {e}")

    def process_email_prompt(self, prompt):
        """Process an email prompt and handle the feedback loop."""
        self.setup_selenium()
        self.close_open_compose_windows()

        recipient = self.extract_recipient(prompt)
        if not recipient:
            self.display_callback("No valid email address found in prompt. Please include one.")
            return

        subject, body = self.generate_email_draft(prompt, recipient)
        current_context = {"recipient": recipient, "subject": subject, "body": body}
        self.display_callback(f"\nDraft:\nRecipient: {recipient}\nSubject: {subject}\nBody: {body}\n")

        if not self.fill_gmail_draft(recipient, subject, body):
            return

        def feedback_loop():
            self.set_feedback_active(True)  # Set flag
            while True:
                self.display_callback("Are you satisfied with this draft? Would you like to make any changes? (yes/no)")
                proceed = self.input_callback().strip().lower()
                if proceed in ['break','exit']:
                    break
                if proceed in ["yes", "no"]:
                    if proceed == "yes":
                        self.send_email()
                        break
                    else:
                        self.display_callback("Please describe the changes you'd like to make to the draft:")
                        new_prompt = self.input_callback().strip()
                        contextual_prompt = f"""
                        The current email draft is as follows:
                        Subject: {current_context['subject']}
                        Body: {current_context['body']}

                        Please update the draft based on the following instructions:
                        {new_prompt}
                        """
                        updated_subject, updated_body = self.generate_email_draft(contextual_prompt, recipient)
                        self.display_callback(f"\nUpdated Draft:\nRecipient: {recipient}\nSubject: {updated_subject}\nBody: {updated_body}\n")
                        if self.update_gmail_draft(updated_subject, updated_body):
                            current_context["subject"] = updated_subject
                            current_context["body"] = updated_body
                        else:
                            break
            self.set_feedback_active(False)  # Reset flag

        threading.Thread(target=feedback_loop, daemon=True).start()

    def cleanup(self):
        """Clean up Selenium driver."""
        if self.driver and self.selenium_initialized:
            self.driver.quit()
            self.selenium_initialized = False