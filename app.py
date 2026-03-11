import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import os
import requests
from fpdf import FPDF # New for PDF Export

# --- 1. PRO APP CONFIG ---
st.set_page_config(page_title="Pure Agency Command", layout="wide", initial_sidebar_state="expanded")

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

# --- 4. THE AI ENGINE ---
def ask_gemini(prompt, system_instruction, image=None):
    try:
        client = genai.Client(api_key=API_KEY)
        contents = [prompt]
        if image: contents.append(image)
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_instruction)
        )
        return response.text
    except Exception as e:
        return f"❌ **Error:** {str(e)}"

# --- 5. AUTOMATION HANDLER (MeisterTask -> SocialPilot) ---
query_params = st.query_params
if "task_topic" in query_params:
    st.success("📥 Automation Request Received")
    mt_topic = query_params["task_topic"]
    mt_brand = query_params.get("brand", "Default")
    mt_date = query_params.get("due_date", "No Date Set")
    
    if mt_brand in st.session_state.clients:
        c_data = st.session_state.clients[mt_brand]
        sys_inst = f"{c_data.get('gem_instructions','')}\n{c_data.get('voice_dna','')}"
        with st.spinner("AI is generating your SocialPilot post..."):
            draft = ask_gemini(f"Write a social media post for: {mt_topic}", sys_inst)
            st.info(f"📅 Scheduled for: {mt_date}")
            st.code(draft)
            st.caption("This text is now sent to the next step in Make.com")
    st.divider()

# --- 6. PDF GENERATOR ---
def create_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=content)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- 7. SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 Elite Command")
mode = st.sidebar.radio("CHOOSE TOOL:", [
    "Manage Clients & Gems",
    "Content & Mockup Factory", 
    "Voice Clone Lab 🎙️",
    "Viral Hook Lab 🔥", 
    "Brand Guardian 🛡️",
    "Strategic Hub (SWOT/Comp)"
])

client_list = list(st.session_state.clients.keys())

# --- TOOL logic ---
if mode == "Manage Clients & Gems":
    st.title("Manage Clients 👤💎")
    with st.form("client_form"):
        name = st.text_input("Brand Name")
        gem = st.text_area("Base Gem Instructions", height=200)
        if st.form_submit_button("Save Brand"):
            st.session_state.clients[name] = {"gem_instructions": gem, "voice_dna": ""}
            save_db(st.session_state.clients)
            st.rerun()
    for b in client_list:
        if st.button(f"Delete {b}"):
            del st.session_state.clients[b]
            save_db(st.session_state.clients)
            st.rerun()

elif not client_list:
    st.warning("Add a brand in 'Manage Clients' first!")

elif mode == "Strategic Hub (SWOT/Comp)":
    st.title("Strategic Analysis Hub 🧠")
    selected = st.selectbox("Select Client:", client_list)
    t1, t2 = st.tabs(["Competitor Analysis", "SWOT Analysis"])
    sys_inst = st.session_state.clients[selected]['gem_instructions']
    
    with t1:
        comp_img = st.file_uploader("Upload Competitor Screenshot", type=["jpg", "png"])
        if st.button("Analyze Competitor"):
            res = ask_gemini("Analyze this competitor move.", sys_inst, Image.open(comp_img) if comp_img else None)
            st.write(res)
            st.download_button("📩 Download PDF Report", create_pdf("Competitor Analysis", res), f"{selected}_Comp_Analysis.pdf")
            
    with t2:
        if st.button("Generate Full SWOT"):
            res = ask_gemini("Generate a full SWOT analysis.", sys_inst)
            st.markdown(res)
            st.download_button("📩 Download PDF Report", create_pdf("SWOT Analysis", res), f"{selected}_SWOT.pdf")

elif mode == "Content & Mockup Factory":
    st.title("Content Factory ✍️📱")
    selected = st.selectbox("Select Brand:", client_list)
    topic = st.text_area("What are we promoting?")
    if st.button("Generate"):
        sys_inst = f"{st.session_state.clients[selected]['gem_instructions']}\n{st.session_state.clients[selected].get('voice_dna','')}"
        st.write(ask_gemini(f"Write a social post about {topic}.", sys_inst))