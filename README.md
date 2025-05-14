Personal AI Assistant 🧠
Status: 🚧 In Progress
A sleek Tkinter-based AI assistant powered by Mistral 7B and Selenium, automating tasks like email drafting and e-commerce searches with multithreading for a responsive UI and real-time updates. Boost your productivity with ease!
Features
Email Automation 📧

What: Draft and send emails via Gmail (e.g., “Send an email to john@example.com”).
Automation:
Threading: LLM generates drafts and Selenium automates Gmail in separate threads, keeping the UI snappy.
Real-Time Updates: Instantly view and refine drafts (e.g., “Make it formal”) in the chat window.


Tech: Mistral LLM, Selenium, queue-based threading.

E-commerce Search (In Progress) 🛒

Goal: Automate product searches on Amazon, Myntra, Flipkart.
Progress:
Fetches Amazon products (name, price, rating, image) with threaded Selenium queries.
Ranks results (cheapest, highest-rated, balanced) and displays with images in Tkinter.
Supports feedback (e.g., “only Amazon, medium price, better pattern”).


Automation: Threaded searches ensure speed; dedicated browser profile enhances privacy.
Next: Add Myntra/Flipkart, clickable purchase links.

Future Plans 🔮

File Organization: Auto-sort files by content (e.g., “organize photos by date”).
Innovations:
📢 Social Media: Schedule posts on X (e.g., “post about my event”).
💸 Budget Tracking: Analyze spending and suggest savings.
📝 Code Review: Auto-suggest code optimizations.
📚 Learning Planner: Craft study schedules with online resources.



Setup 🛠️

Clone: git clone <repo-url>

Install: pip install -r requirements.txt

Add .env:
MISTRAL_API_KEY=<your-key>


Install Brave browser and chromedriver.

Run: python assistant.py


Structure 📂

assistant.py: Tkinter UI, query routing.
emails_utils.py: Email drafting/sending.
ecommerce_utils.py: E-commerce searches.
Dependencies: tkinter, mistralai, selenium, undetected-chromedriver, Pillow, requests.

Notes 📝

In Progress: E-commerce expanding, new features coming!
Contribute: Share ideas for automations!

Adding a Video 🎥
To showcase a demo or tutorial, add a video to the README using one of these methods:

YouTube/Vimeo Link: Upload to YouTube or Vimeo and embed with a markdown link:
[Watch the Demo](https://www.youtube.com/watch?v=your-video-id)


GIF for GitHub: Convert a short video to a GIF (use tools like ezgif.com), upload to your GitHub repo, and embed:
![Demo GIF](path/to/demo.gif)


Hosted Video: Host an MP4 on GitHub or a CDN, but note that markdown doesn’t support direct video embedding. Use an image link to the video:
[![Demo Video](path/to/thumbnail.png)](path/to/video.mp4)


Tip: For GitHub, GIFs work best for seamless display. Keep videos short (<10s) for quick loading.


License 📜
MIT License
