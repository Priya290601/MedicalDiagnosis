# MedicalDiagnosis
<img width="1536" height="1024" alt="ChatGPT Image Feb 10, 2026, 12_57_21 PM" src="https://github.com/user-attachments/assets/2a800853-fe33-48ad-a926-652216926fa1" />

🩺 AI Medical Diagnosis Tool
An AI-powered Medical Image & Report Analysis System built using Streamlit (Frontend) and AGNO Agent + Google Gemini (Backend AI Engine).
This application allows users to:
📸 Upload medical images (X-ray, MRI, CT, etc.)
📝 Paste or upload medical reports (TXT, PDF, DOCX)
🤖 Get structured AI-based diagnostic analysis
📊 Visualize diagnosis confidence levels
🔎 Fetch research references using live web search

🏗️ Architecture Overview
🔹 Frontend: Streamlit UI
The frontend is built using Streamlit, which handles:
File uploads (Image/Report)
Text input
Buttons (Analyze Image / Analyze Report)
Displaying AI-generated report
Showing confidence graph using Matplotlib

Streamlit acts as both:
UI Layer
Request Handler

🔹 Backend: AI Agent Layer
The backend logic is handled by:
AGNO Agent Framework
Google Gemini Model (gemini-2.0-flash-exp)
DuckDuckGo Search Tool

Backend Responsibilities:
Image processing & resizing
Sending structured prompts to Gemini
Web search for medical references
Generating structured markdown response
Returning diagnosis with confidence %
Providing research-backed references

🔄 How Frontend is Connected to Backend
Even though this is a single Python application, the architecture follows a logical frontend-backend separation.

Step-by-Step Flow
🖼️ Image Analysis Flow
User uploads image in Streamlit UI.
Streamlit saves image temporarily.
analyze_medical_image() function is triggered.
Image is resized using PIL.
Image is converted into AgnoImage.

The image + structured query is sent to:
medical_agent.run(query, images=[agno_image])

Gemini processes:
Image understanding
Medical reasoning
Web search via DuckDuckGo
Backend returns structured markdown response.

Streamlit displays:
Diagnosis report
Extracted confidence levels
Horizontal bar chart

📝 Text Report Analysis Flow
User pastes text or uploads report file.
File is read using:
fitz (PDF)
docx
Plain text reader
analyze_text_report() sends text to:
medical_agent.run(text)

Gemini analyzes report.
Structured response is returned.
Confidence values are extracted using Regex.
Streamlit visualizes confidence graph.

📊 Confidence Extraction Logic
The system extracts diagnosis confidence using regex:
pattern = r"([A-Za-z\\s\\-]+)\\s*\\(Confidence[:]? (\\d+)%\\)"

Expected AI Output Format:
Pneumonia (Confidence: 85%)

This enables automatic parsing and graph generation.

🧠 Backend Intelligence
The AI agent is configured as:
medical_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[DuckDuckGoTools()],
    markdown=True
)
It enables:
Multimodal understanding (Text + Image)
Web search for latest treatment protocols
Structured markdown output
Evidence-based diagnostic reasoning

📦 Tech Stack
Layer	Technology Used
UI	Streamlit
AI Model	Google Gemini 2.0 Flash
Agent Layer	AGNO Agent Framework
Web Search	DuckDuckGoTools
Image Processing	Pillow
PDF Reader	PyMuPDF
DOCX Reader	python-docx
Visualization	Matplotlib

🚀 How to Run the Project
1️⃣ Clone Repository
git clone https://github.com/yourusername/medicaldiagnosis.git
cd medicaldiagnosis

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Set Google API Key
Replace inside the code:
GOOGLE_API_KEY = "YOUR_API_KEY"

OR set environment variable:
export GOOGLE_API_KEY="your_api_key"
(Windows)
set GOOGLE_API_KEY=your_api_key

4️⃣ Run Application
streamlit run medical.py

🔐 Security Note

⚠️ Do NOT hardcode API keys in production.
Use environment variables or .env file.

🧩 Is This Really Frontend + Backend?
Yes — logically.

📈 Future Enhancements
Add authentication system
Store reports in database
Add patient history tracking
Deploy on AWS / Azure
Convert to microservices architecture
Add RAG-based medical knowledge base
