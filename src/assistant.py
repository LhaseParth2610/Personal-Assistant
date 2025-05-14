# import tkinter as tk
# from tkinter import ttk
# import re
# from mistralai import Mistral
# from dotenv import load_dotenv
# import os
# from emails_utils import EmailAssistant
# from ecommerce_utils import EcommerceAssistant
# import threading
# import queue
# import json
# from PIL import Image, ImageTk
# import requests
# import io

# # Load environment variables
# load_dotenv()
# api_key = os.getenv("MISTRAL_API_KEY")

# class ChatApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("IdiotAid Chat")
#         self.root.geometry("600x700")
#         self.root.attributes('-topmost', True)
#         self.input_queue = queue.Queue()
#         self.email_assistant = None
#         self.ecommerce_assistant = None
#         self.results_window = None
#         self.image_refs = []  # Store image references

#         # Color scheme and fonts
#         self.text_color = "#FFFFFF"
#         self.user_bubble_color = "#7289DA"
#         self.assistant_bubble_color = "#23272A"
#         self.input_bg = "#40444B"
#         self.font = ("Helvetica", 12)
#         self.bubble_font = ("Helvetica", 11)

#         # Configure root window
#         self.root.minsize(400, 500)

#         # Create gradient background
#         self.create_gradient_background()

#         # Main frame
#         self.main_frame = tk.Frame(self.root)
#         self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

#         # Chat display
#         self.chat_canvas = tk.Canvas(self.main_frame, highlightthickness=0)
#         self.chat_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.chat_canvas.yview)
#         self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)
#         self.chat_scrollbar.pack(side="right", fill="y")
#         self.chat_canvas.pack(side="left", fill="both", expand=True)
#         self.chat_frame = tk.Frame(self.chat_canvas)
#         self.chat_window = self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
#         self.chat_frame.bind("<Configure>", self._update_canvas)
#         self.chat_canvas.bind("<Configure>", self._resize_canvas)
#         self.root.bind("<MouseWheel>", self._on_mousewheel)
#         self.root.protocol("WM_DELETE_WINDOW", self.on_close)

#         # Input frame
#         self.input_frame = tk.Frame(self.root)
#         self.input_frame.pack(fill="x", padx=10, pady=(0, 10))
#         self.input_field = tk.Entry(
#             self.input_frame, bg=self.input_bg, fg=self.text_color, font=self.font,
#             insertbackground=self.text_color, relief="flat", borderwidth=2
#         )
#         self.input_field.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=5)
#         self.send_button = tk.Button(
#             self.input_frame, text="Send", command=self.process_input,
#             bg=self.user_bubble_color, fg=self.text_color, font=self.font,
#             relief="flat", activebackground="#5B6EAE", cursor="hand2"
#         )
#         self.send_button.pack(side="right")
#         self.input_field.bind("<Return>", self.process_input)

#         # Initialize assistants
#         self.email_assistant = EmailAssistant(self.display_message, self.get_input)
#         self.ecommerce_assistant = EcommerceAssistant(self.display_message, self.get_input)

#         # Welcome message
#         self.display_message("IdiotAid: How may I help you today? Type 'exit' to quit.")

#     def create_gradient_background(self):
#         """Create a gradient background for the root window."""
#         self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
#         self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
#         colors = ["#4B0082", "#6A5ACD", "#483D8B", "#7B68EE"]
#         height = 700
#         segments = len(colors) - 1
#         segment_height = height // segments
#         for i in range(segments):
#             y1 = i * segment_height
#             y2 = (i + 1) * segment_height
#             self.bg_canvas.create_rectangle(0, y1, 600, y2, fill=colors[i], outline="")
#         def update_gradient(event):
#             self.bg_canvas.delete("all")
#             height = event.height
#             segment_height = height // segments
#             for i in range(segments):
#                 y1 = i * segment_height
#                 y2 = (i + 1) * segment_height
#                 self.bg_canvas.create_rectangle(0, y1, event.width, y2, fill=colors[i], outline="")
#         self.root.bind("<Configure>", update_gradient)

#     def _update_canvas(self, event):
#         """Update canvas scroll region."""
#         self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

#     def _resize_canvas(self, event):
#         """Resize chat window to fit canvas width."""
#         canvas_width = event.width
#         self.chat_canvas.itemconfig(self.chat_window, width=canvas_width)

#     def _on_mousewheel(self, event):
#         """Handle mouse wheel scrolling."""
#         self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

#     def display_message(self, message):
#         """Display a message in a chat bubble."""
#         is_user = message.startswith("You: ")
#         bubble_color = self.user_bubble_color if is_user else self.assistant_bubble_color
#         text_color = self.text_color
#         anchor = "e" if is_user else "w"
#         justify = "right" if is_user else "left"
#         padx = (10, 50) if is_user else (50, 10)
#         text = message[5:] if is_user else message
#         bubble_frame = tk.Frame(self.chat_frame)
#         bubble_frame.pack(fill="x", padx=padx, pady=5)
#         bubble = tk.Label(
#             bubble_frame, text=text, bg=bubble_color, fg=text_color, font=self.bubble_font,
#             wraplength=400, justify=justify, anchor=anchor, padx=10, pady=5,
#             relief="raised", borderwidth=1, highlightbackground="#000000", highlightthickness=1
#         )
#         bubble.pack(anchor=anchor)
#         self.chat_canvas.update_idletasks()
#         self.chat_canvas.yview_moveto(1.0)

#     def get_input(self):
#         """Get input from the input queue."""
#         self.input_field.delete(0, tk.END)
#         self.input_field.focus_set()
#         while True:
#             try:
#                 return self.input_queue.get(block=True)
#             except queue.Empty:
#                 self.root.update()
#                 continue

#     def on_close(self):
#         """Handle the window close event."""
#         self.email_assistant.cleanup()
#         if self.ecommerce_assistant:
#             self.ecommerce_assistant.cleanup()
#         self.root.destroy()

#     def show_ecommerce_results(self, amazon_results, myntra_results, flipkart_results):
#         """Display e-commerce results with images in a separate window."""
#         if self.results_window and self.results_window.winfo_exists():
#             self.results_window.destroy()

#         self.results_window = tk.Toplevel(self.root)
#         self.results_window.title("E-commerce Results")
#         self.results_window.geometry("1000x600")

#         main_frame = tk.Frame(self.results_window)
#         main_frame.pack(fill="both", expand=True, padx=10, pady=10)

#         for idx, (site, results) in enumerate([
#             ("Amazon", amazon_results),
#             ("Myntra", myntra_results),
#             ("Flipkart", flipkart_results)
#         ]):
#             frame = tk.LabelFrame(main_frame, text=site, font=("Helvetica", 12))
#             frame.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")

#             tree = ttk.Treeview(frame, columns=("Image", "Name", "Price", "Rating", "URL"), show="headings")
#             tree.heading("Image", text="Image")
#             tree.heading("Name", text="Product")
#             tree.heading("Price", text="Price")
#             tree.heading("Rating", text="Rating")
#             tree.heading("URL", text="Link")
#             tree.column("Image", width=100, anchor="center")
#             tree.column("Name", width=150)
#             tree.column("Price", width=80)
#             tree.column("Rating", width=80)
#             tree.column("URL", width=100)
#             tree.pack(fill="both", expand=True)

#             for result in results[:5]:
#                 try:
#                     img_data = requests.get(result.get("image_url", "")).content
#                     img = Image.open(io.BytesIO(img_data))
#                     img = img.resize((50, 50), Image.Resampling.LANCZOS)
#                     photo = ImageTk.PhotoImage(img)
#                     self.image_refs.append(photo)

#                     tree.insert("", "end", values=(
#                         "",
#                         result.get("name", "N/A"),
#                         f"${result.get('price', 0):.2f}",
#                         f"{result.get('rating', 0)} stars",
#                         result.get("url", "N/A")
#                     ), image=photo)
#                 except:
#                     tree.insert("", "end", values=(
#                         "No Image",
#                         result.get("name", "N/A"),
#                         f"${result.get('price', 0):.2f}",
#                         f"{result.get('rating', 0)} stars",
#                         result.get("url", "N/A")
#                     ))

#         feedback_frame = tk.Frame(main_frame)
#         feedback_frame.grid(row=1, column=0, columnspan=3, pady=10)
#         tk.Label(feedback_frame, text="Satisfied? Need more options? (e.g., 'only Amazon, medium price, better pattern')").pack()
#         feedback_entry = tk.Entry(feedback_frame)
#         feedback_entry.pack(fill="x", padx=5)
#         feedback_entry.bind("<Return>", lambda event: self.handle_feedback(feedback_entry.get(), amazon_results, myntra_results, flipkart_results))

#     def handle_feedback(self, feedback, amazon_results, myntra_results, flipkart_results):
#         """Handle user feedback for refined e-commerce queries."""
#         self.display_message(f"You: {feedback}")
#         self.input_queue.put(feedback)
#         if feedback.lower() not in ["satisfied", "yes"]:
#             threading.Thread(
#                 target=self.ecommerce_assistant.process_feedback_query,
#                 args=(feedback, amazon_results, myntra_results, flipkart_results),
#                 daemon=True
#             ).start()

#     def process_input(self, event=None):
#         """Process user input from the input field."""
#         user_input = self.input_field.get().strip()
#         if not user_input:
#             return

#         self.display_message(f"You: {user_input}")
#         self.input_queue.put(user_input)
#         self.input_field.delete(0, tk.END)

#         if user_input.lower() in ('exit', 'break'):
#             self.email_assistant.cleanup()
#             if self.ecommerce_assistant:
#                 self.ecommerce_assistant.cleanup()
#             self.root.quit()
#             return

#         if self.email_assistant.feedback_active and user_input.lower() in ('yes', 'no'):
#             return

#         email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
#         if re.search(email_pattern, user_input):
#             threading.Thread(target=self.email_assistant.process_email_prompt, args=(user_input,), daemon=True).start()
#         else:
#             with Mistral(api_key=api_key) as client:
#                 prompt = f"""
#                 Classify if the query is an e-commerce request. Return JSON:
#                 {{ "is_ecommerce": bool, "product": str or null, "budget": float or null }}
#                 Query: {user_input}
#                 """
#                 resp = client.chat.complete(
#                     model="open-mistral-7b",
#                     messages=[{"role": "user", "content": prompt}]
#                 )
#                 try:
#                     intent = json.loads(resp.choices[0].message.content)
#                 except:
#                     intent = {"is_ecommerce": False, "product": None, "budget": None}

#             if intent["is_ecommerce"]:
#                 threading.Thread(
#                     target=self.ecommerce_assistant.process_product_query,
#                     args=(user_input, self.show_ecommerce_results),
#                     daemon=True
#                 ).start()
#             else:
#                 self.process_general_query(user_input)

#     def process_general_query(self, prompt):
#         """Process a general LLM query using Mistral."""
#         def query_llm():
#             with Mistral(api_key=api_key) as client:
#                 response = client.chat.complete(
#                     model="open-mistral-7b",
#                     messages=[{"role": "user", "content": prompt}]
#                 )
#                 self.display_message(f"IdiotAid: {response.choices[0].message.content}")
#         threading.Thread(target=query_llm, daemon=True).start()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ChatApp(root)
#     root.mainloop()
import tkinter as tk
from tkinter import ttk
import re
from mistralai import Mistral
from dotenv import load_dotenv
import os
from emails_utils import EmailAssistant
import threading
import queue
import sys

# Load environment variables
load_dotenv()
API_KEY = os.getenv("MISTRAL_API_KEY")

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IdiotAid Chat")
        self.root.geometry("600x700")
        self.root.attributes('-topmost', True)

        # Shared queue: only feedback/instructions go here now
        self.input_queue = queue.Queue()

        # Your existing EmailAssistant
        self.email_assistant = EmailAssistant(
            display_callback=self.display_message,
            input_callback=lambda: self.input_queue.get(block=True)
        )

        # UI colors & fonts
        self.text_color = "#FFFFFF"
        self.user_bubble_color = "#7289DA"
        self.assistant_bubble_color = "#23272A"
        self.input_bg = "#40444B"
        self.font = ("Helvetica", 12)
        self.bubble_font = ("Helvetica", 11)

        self._create_widgets()
        self.display_message("IdiotAid: How may I help you today? Type 'exit' to quit.")

    def _create_widgets(self):
        # Gradient background
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._draw_gradient()
        self.root.bind("<Configure>", lambda e: self._draw_gradient())

        # Chat area
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        self.chat_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)
        self.chat_scrollbar.pack(side="right", fill="y")
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.chat_frame = tk.Frame(self.chat_canvas)
        self.chat_window = self.chat_canvas.create_window((0,0), window=self.chat_frame, anchor="nw")
        self.chat_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.bind("<Configure>", lambda e: self.chat_canvas.itemconfig(self.chat_window, width=e.width))
        self.root.bind("<MouseWheel>", lambda e: self.chat_canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

        # Close handling
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Input area
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill="x", padx=10, pady=(0,10))
        self.input_field = tk.Entry(
            self.input_frame, bg=self.input_bg, fg=self.text_color, font=self.font,
            insertbackground=self.text_color, relief="flat", borderwidth=2
        )
        self.input_field.pack(side="left", fill="x", expand=True, padx=(0,10), ipady=5)
        self.send_button = tk.Button(
            self.input_frame, text="Send", command=self.process_input,
            bg=self.user_bubble_color, fg=self.text_color, font=self.font,
            relief="flat", activebackground="#5B6EAE", cursor="hand2"
        )
        self.send_button.pack(side="right")
        self.input_field.bind("<Return>", self.process_input)

    def _draw_gradient(self):
        self.bg_canvas.delete("all")
        colors = ["#4B0082", "#6A5ACD", "#483D8B", "#7B68EE"]
        h = self.root.winfo_height() or 700
        seg = len(colors)-1
        sh = h//seg
        for i, c in enumerate(colors[:-1]):
            self.bg_canvas.create_rectangle(0, i*sh, self.root.winfo_width(), (i+1)*sh,
                                            fill=c, outline="")

    def display_message(self, message):
        is_user = message.startswith("You: ")
        bubble_color = self.user_bubble_color if is_user else self.assistant_bubble_color
        anchor = "e" if is_user else "w"
        justify = "right" if is_user else "left"
        padx = (10,50) if is_user else (50,10)
        text = message[5:] if is_user else message

        frame = tk.Frame(self.chat_frame)
        frame.pack(fill="x", padx=padx, pady=5)
        lbl = tk.Label(frame, text=text, bg=bubble_color, fg=self.text_color,
                       font=self.bubble_font, wraplength=400,
                       justify=justify, anchor=anchor,
                       padx=10, pady=5, relief="raised", borderwidth=1)
        lbl.pack(anchor=anchor)
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def on_close(self):
        # Unblock any pending feedback thread
        self.input_queue.put("exit")
        self.email_assistant.cleanup()
        self.root.destroy()
        sys.exit(0)

    def process_input(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        # Echo user
        self.display_message(f"You: {user_input}")
        self.input_field.delete(0, tk.END)

        # Exit shortcut
        if user_input.lower() == "exit":
            return self.on_close()

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        # If an email-feedback session is already running, *only* enqueue for it
        if self.email_assistant.feedback_active:
            self.input_queue.put(user_input)
            return

        # If it’s a new email request, *do not* enqueue—directly start the thread
        if re.search(email_pattern, user_input):
            threading.Thread(
                target=self.email_assistant.process_email_prompt,
                args=(user_input,),
                daemon=True
            ).start()
            return

        # Otherwise treat it as a normal LLM query
        threading.Thread(
            target=self._general_query,
            args=(user_input,),
            daemon=True
        ).start()

    def _general_query(self, prompt):
        with Mistral(api_key=API_KEY) as client:
            resp = client.chat.complete(
                model="open-mistral-7b",
                messages=[{"role":"user","content":prompt}]
            )
            answer = resp.choices[0].message.content
        self.display_message(f"IdiotAid: {answer}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
