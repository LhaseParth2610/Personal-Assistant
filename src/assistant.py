import tkinter as tk
from tkinter import scrolledtext
from emails_utils import main as email_main
from llm_utils import process_prompt  # Function to handle LLM-related prompts

def handle_user_input():
    """Handle user input and route it to the appropriate module."""
    user_input = input_box.get()
    chat_area.insert(tk.END, f"You: {user_input}\n")
    input_box.delete(0, tk.END)

    # Process the input
    if "email" in user_input.lower():
        chat_area.insert(tk.END, "Assistant: Opening email module...\n")
        email_main()  # Call the email module
    else:
        # Process other prompts using the LLM
        response = process_prompt(user_input)
        chat_area.insert(tk.END, f"Assistant: {response}\n")

# Create the main window
root = tk.Tk()
root.title("IdiotAid Assistant")
root.geometry("500x600")
root.resizable(False, False)

# Chat area
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=25, width=60)
chat_area.pack(pady=10)
chat_area.insert(tk.END, "Assistant: How can I help you today?\n")

# Input box
input_box = tk.Entry(root, width=50)
input_box.pack(pady=5)

# Send button
send_button = tk.Button(root, text="Send", command=handle_user_input)
send_button.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()