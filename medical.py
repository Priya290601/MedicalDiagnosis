import os
import re
import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image as PILImage
import docx
import fitz  # PyMuPDF for PDF reading
# AGNO AI imports 
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.media import Image as AgnoImage
# Set your API Key
GOOGLE_API_KEY = "AIzaSyAEVjjK4nY9kldGd5BrLxqaR6OEOqX2GSA"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
#Ensure API key is provided
if not GOOGLE_API_KEY:
    raise ValueError("⚠️ Please set your Google API Key in GOOGLE_API_KEY")
# Initialize the Medical Agent
medical_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[DuckDuckGoTools()],
    markdown=True
)
# Medical Analysis Query Template
query = """
You are a highly skilled medical imaging expert with extensive knowledge in radiology and diagnostic imaging. Analyze the medical image and structure your response as follows:
### 1. Image Type & Region
- Identify imaging modality (X-ray/MRI/CT/Ultrasound/etc.).
- Specify anatomical region and positioning.
- Evaluate image quality and technical adequacy.

### 2. Key Findings
- Highlight primary observations systematically.
- Identify potential abnormalities with detailed descriptions.
- Include measurements and densities where relevant.

### 3. Diagnostic Assessment
- Provide primary diagnosis with confidence level in %**
- Format: Diagnosis Name (Confidence: XX%) (use exactly this format so it can be parsed).
- List differential diagnoses ranked by likelihood.
- Support each diagnosis with observed evidence.
- Highlight critical/urgent findings.

### 4. Patient-Friendly Explanation
- Simplify findings in clear, non-technical language.
- Avoid medical jargon or provide easy definitions.
- Include relatable visual analogies.

### 5. Research Context
- Use DuckDuckGo search to find recent medical literature.
- Search for standard treatment protocols.
- Provide 2-3 key references supporting the analysis.

Ensure a structured and medically accurate response using clear markdown formatting.
"""
# Analyze medical image
def analyze_medical_image(image_path):
    """Processes and analyzes a medical image using AI"""
    #Open and resize image
    image = PILImage.open(image_path)
    width, height = image.size
    aspect_ratio = width / height
    new_width = 500
    new_height = int(new_width / aspect_ratio)
    resized_image = image.resize((new_width, new_height))
    #Save resized image
    temp_path = "temp_resized_image.png"
    resized_image.save(temp_path)
    #Create AgnoImage object
    agno_image = AgnoImage(filepath=temp_path)
    #Run AI analysis
    try:
        response = medical_agent.run(query, images=[agno_image])
        return response.content
    except Exception as e:
        return f"⚠️ Analysis error: {e}"
    finally:
        #Clean up temporary file 
        os.remove(temp_path)
# Analyze text report
def analyze_text_report(text):
    if not text.strip():
        return "⚠️ Text report is empty."
    if len(text) > 10000:
        return "⚠️ Text report is too long. Please shorten it to under 10,000 characters."
    try:
        response = medical_agent.run(text)
        return response.content
    except Exception as e:
        return f"⚠️ Text analysis error: {e}"
# Extract diagnosis confidence
def extract_confidences_from_report(report_text):
    pattern = r"([A-Za-z\\s\\-]+)\\s*\\(Confidence[:]? (\\d+)%\\)"
    matches = re.findall(pattern, report_text)
    labels = [label.strip() for label, _ in matches]
    confidences = [int(conf)/100 for _, conf in matches]
    return labels, confidences
# Read uploaded report file
def read_uploaded_report(file):
    try:
        if file.type == "text/plain":
            return file.read().decode("utf-8")
        elif file.type == "application/pdf":
            doc = fitz.open(stream=file.read(), filetype="pdf")
            return "\n".join([page.get_text() for page in doc])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(file)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return None
    except Exception as e:
        return f"⚠️ Error reading report file: {e}"
    

# Streamlit UI setup
st.set_page_config(page_title="Medical Diagnosis", layout="centered")
st.title("🩺 Medical Diagnosis Tool 🔬")
st.markdown("""
Welcome to the **Medical Diagnosis** tool! 📸📝  
You can now upload a **Medical Image** or **Paste/Upload a Medical Report** for AI-powered analysis.  
Let's get started!
""")
# Sidebar Upload image
st.sidebar.header("Upload Your Medical Image:")
uploaded_file = st.sidebar.file_uploader("Choose a medical image file", type=["jpg", "jpeg", "png", "bmp", "gif"])
#Sidebar Paste text report
st.sidebar.header("Or Paste a Medical Report:")
text_report = st.sidebar.text_area("Enter medical report text here", height=100)
#Sidebar Upload report
st.sidebar.header("Or Upload a Medical Report File:")
uploaded_report_file = st.sidebar.file_uploader("Choose a report file", type=["txt", "pdf", "docx"])
#Button to Image analysis
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    #Display the uploaded image in Streamlit
    if st.sidebar.button("Analyze Image"):
        with st.spinner("🔍 Analyzing the image... Please wait."):
             #Save the uploaded image to a temporary file
            image_path = f"temp_image.{uploaded_file.type.split('/')[1]}"
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            #Run analysis on the uploaded image
            report = analyze_medical_image(image_path)
            #Display the report
            st.subheader("📋 Analysis Report")
            st.markdown(report, unsafe_allow_html=True)
            #Extract and display confidence level
            labels, confidences = extract_confidences_from_report(report)
            if labels and confidences:
                st.subheader("📊 Diagnosis Confidence Levels")
                fig, ax = plt.subplots()
                ax.barh(labels, confidences, color='skyblue')
                ax.set_xlim(0, 1)
                ax.set_xlabel("Confidence Level")
                ax.set_title("Diagnosis Likelihood")
                st.pyplot(fig)
            else:
                st.info("ℹ️ No confidence scores found in the report.")
            #Clean up the saved image    
            os.remove(image_path)
#Text report analysis
elif text_report or uploaded_report_file:
    #Anlaysis when the sidebar button is clicked
    if st.sidebar.button("Analyze Text Report"):
        with st.spinner("🧠 Analyzing the text report... Please wait."):
            #Read the uploaded report file or use pasted text
            if uploaded_report_file:
                text = read_uploaded_report(uploaded_report_file)
            else:
                text = text_report
            #Analyze thre text report and display the result
            if text:
                report = analyze_text_report(text)
                st.subheader("📋 Text Report Analysis")
                st.markdown(report, unsafe_allow_html=True)
                #Extract and visualize diagnosis confidence level
                labels, confidences = extract_confidences_from_report(report)
                if labels and confidences:
                    st.subheader("📊 Diagnosis Confidence Levels")
                    fig, ax = plt.subplots()
                    ax.barh(labels, confidences, color='lightgreen')
                    ax.set_xlim(0, 1)
                    ax.set_xlabel("Confidence Level")
                    ax.set_title("Diagnosis Likelihood")
                    st.pyplot(fig)
                else:
                    #if no confidence scores are found
                    st.info("ℹ️ No confidence scores found in the report.")
            else:
                st.error("⚠️ Could not read the uploaded report file.")                
#Prompt user to provide input if nothing is uploaded or pasted
else:
    st.warning("⚠️ Please upload a medical image or paste/upload a report to begin analysis.")
