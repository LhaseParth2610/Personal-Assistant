# 🧠 Personal AI Assistant  
Personal Assistant who makes your life way easier than it already is :D

**Status:** 🚧 *In Progress*  

A sleek **Tkinter-based AI assistant** powered by **Mistral 7B** and **Selenium**, automating tasks like email drafting and e-commerce searches with multithreading for a responsive UI and real-time updates.  
**Boost your productivity with ease!**

---

## ✨ Features

### 📧 Email Automation
- **What it does:**  
  Drafts and sends emails via Gmail using natural language (e.g., *“Send an email to john@example.com”*).
- **Automation Highlights:**
  - **Threading:** Keeps UI responsive by running LLM and Selenium automation in separate threads.
  - **Real-Time Updates:** Instantly view and refine drafts (e.g., *“Make it formal”*) in the chat window.

> **Tech:** `Mistral LLM`, `Selenium`, `queue-based threading`

### Watch how it works
[▶️ Watch the Demo](https://youtu.be/BGT5XcpqUjg)

---

### 🛒 E-commerce Search *(In Progress)*
- **Goal:** Automate product searches on platforms like **Amazon**, **Myntra**, and **Flipkart**.
- **Current Capabilities:**
  - Fetches Amazon products (name, price, rating, image).
  - Uses **threaded Selenium queries** for speed.
  - Displays results in Tkinter with images and feedback options (e.g., *“only Amazon, medium price, better pattern”*).
- **Coming Soon:**
  - Add Myntra & Flipkart support.
  - Clickable purchase links.

> **Automation:** Threaded searches + dedicated browser profile for enhanced privacy

---

## 🔮 Future Plans

| Feature            | Description                                                |
|--------------------|------------------------------------------------------------|
| 🗂️ File Organizer   | Auto-sort files by content (e.g., “organize photos by date”) |
| 📢 Social Media     | Schedule posts (e.g., *“post about my event on X”*)         |
| 💸 Budget Tracker   | Analyze spending, suggest savings                          |
| 🧠 Code Review      | Auto-suggest code improvements                              |
| 📚 Learning Planner | Plan study schedules + recommend online resources          |

---

## 🛠️ Setup

1. **Clone the repo**  
   ```bash
   git clone <repo-url>
