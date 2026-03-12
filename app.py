import streamlit as st
import time
from google import genai
from google.genai import types
from PIL import Image
import json
import os
import requests
from fpdf import FPDF

# --- 1. PRO APP CONFIG ---
st.set_page_config(
    page_title="Pure Agency Command", 
    page_icon="🚀",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. THE LOGIN GATE ---
if "password_correct" not in st.session_state:
    st.title("🔐 Agency Command Center")
    pwd = st.text_input("Enter Agency Access Code:", type="password")
    if st.button("Unlock Command Center"):
        if pwd == st.secrets["AGENCY_PASSWORD"]:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Access Denied")
    st.stop()

# --- 3. DATABASE & API SETUP ---
API_KEY = st.secrets["GEMINI_API_KEY"]
DB_FILE = "client_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if "clients" not in st.session_state:
    st.session_state.clients = load_db()

# --- 4. THE AI ENGINE (Optimized for Paid Tier) ---
def ask_gemini(prompt, system_instruction, image=None):
    client = genai.Client(api_key=API_KEY)
    contents = [prompt]
    if image: contents.append(image)
    
    # Retry logic for 429/busy errors
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash', # Corrected stable model ID
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=system_instruction)
            )
            return response.text
        except Exception as e:
            if "429" in str(e):
                time.sleep(3)
                continue
            return f"❌ AI Error: {str(e)}"
    return "❌ Error: System busy. Please try again in 60 seconds."

# --- 5. PDF GENERATOR ---
def create_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    # Clean text for PDF compatibility (removes emojis/unsupported symbols)
    safe_text = content.encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 10, txt=safe_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 6. SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 Elite Command")
mode = st.sidebar.radio("CHOOSE TOOL:", [
    "Manage Clients & Gems",
    "Content Factory ✍️", 
    "6-Month Strategy Lab 📅",
    "Voice Clone Lab 🎙️",
    "Viral Hook Lab 🔥", 
    "Brand Guardian 🛡️",
    "Strategic Hub (SWOT/Comp)"
])

client_list = list(st.session_state.clients.keys())

# --- 7. AUTOMATION RECEIVER (Hidden Bridge) ---
query_params = st.query_params
if "task_topic" in query_params:
    st.info(f"📥 New Task from MeisterTask: {query_params['task_topic']}")

# --- 8. TOOL LOGIC ---

if mode == "Manage Clients & Gems":
    st.title("Manage Clients 👤💎")
    with st.form("client_form"):
        name = st.text_input("Brand Name")
        gem = st.text_area("Base Gem Instructions (Voice, Tone, Rules)", height=200)
        if st.form_submit_button("Save Brand"):
            if name:
                st.session_state.clients[name] = {"gem_instructions": gem, "voice_dna": ""}
                save_db(st.session_state.clients)
                st.success(f"Saved {name} successfully!")
                st.rerun()

    st.divider()
    for b in client_list:
        col1, col2 = st.columns([4,1])
        col1.write(f"🏢 {b}")
        if col2.button(f"Delete", key=f"del_{b}"):
            del st.session_state.clients[b]
            save_db(st.session_state.clients)
            st.rerun()

elif not client_list:
    st.warning("Please add a client brand in 'Manage Clients' first.")

elif mode == "Content Factory ✍️":
    st.title("Content Factory ✍️")
    selected = st.selectbox("Select Brand:", client_list)
    topic = st.text_area("What are we promoting?")
    if st.button("Generate Post", type="primary"):
        sys = f"{st.session_state.clients[selected]['gem_instructions']}\n{st.session_state.clients[selected].get('voice_dna','')}"
        with st.spinner("AI is thinking..."):
            st.write(ask_gemini(f"Write a social media post about {topic}", sys))

elif mode == "6-Month Strategy Lab 📅":
    st.title("Strategy Lab 📅")
    selected = st.selectbox("Select Client:", client_list)
    months = st.select_slider("Timeline:", options=["1 Month", "2 Months", "3 Months", "6 Months"])
    goal = st.text_input("Primary Strategic Goal:")
    if st.button(f"Generate {months} Strategy", type="primary"):
        with st.spinner(f"Building your {months} roadmap..."):
            res = ask_gemini(f"Create a high-level {months} content roadmap for: {goal}", st.session_state.clients[selected]['gem_instructions'])
            st.markdown(res)
            st.download_button("📩 Download PDF Strategy", create_pdf(f"{months} Plan", res), f"{selected}_Strategy.pdf")

elif mode == "Voice Clone Lab 🎙️":
    st.title("Voice Clone Lab 🎙️")
    selected = st.selectbox("Analyze Voice for:", client_list)
    posts = st.text_area("Paste 3 successful posts here:", height=200)
    if st.button("Extract Style DNA"):
        dna = ask_gemini(f"Extract the linguistic DNA and tone from these posts: {posts}", "Expert Linguist")
        st.session_state.clients[selected]['voice_dna'] = dna
        save_db(st.session_state.clients)
        st.success("Linguistic DNA Captured!")
        st.write(dna)

elif mode == "Viral Hook Lab 🔥":
    st.title("Viral Hook Lab 🔥")
    selected = st.selectbox("Select Brand Context:", client_list)
    topic = st.text_input("Headline/Topic:")
    if st.button("Generate 10 Hooks"):
        st.write(ask_gemini(f"Generate 10 viral hooks for: {topic}", st.session_state.clients[selected]['gem_instructions']))

elif mode == "Brand Guardian 🛡️":
    st.title("Brand Guardian 🛡️")
    selected = st.selectbox("Audit Client:", client_list)
    img = st.file_uploader("Upload Image/Graphic", type=["png", "jpg"])
    if st.button("Run Audit") and img:
        st.info(ask_gemini("Audit this image for brand consistency.", st.session_state.clients[selected]['gem_instructions'], Image.open(img)))

elif mode == "Strategic Hub (SWOT/Comp)":
    st.title("Strategic Hub 🧠")
    selected = st.selectbox("Analyze Client:", client_list)
    t1, t2 = st.tabs(["Competitor Move", "Full SWOT"])
    with t1:
        c_img = st.file_uploader("Competitor Post", type=["png", "jpg"])
        if st.button("Analyze Move"):
            st.write(ask_gemini("Analyze this competitor and give us a counter-move.", st.session_state.clients[selected]['gem_instructions'], Image.open(c_img) if c_img else None))
    with t2:
        if st.button("Run SWOT Analysis"):
            res = ask_gemini("Generate a full SWOT analysis report.", st.session_state.clients[selected]['gem_instructions'])
            st.markdown(res)
            st.download_button("📩 Download SWOT PDF", create_pdf("SWOT Report", res), f"{selected}_SWOT.pdf")