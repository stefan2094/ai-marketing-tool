import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import os
import requests
from fpdf import FPDF

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

# --- 5. PDF GENERATOR ---
def create_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
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

# --- TOOL 1: MANAGE CLIENTS (Always visible) ---
if mode == "Manage Clients & Gems":
    st.title("Manage Clients 👤💎")
    with st.form("client_form"):
        name = st.text_input("Brand Name")
        gem = st.text_area("Base Gem Instructions (Tone, Target, Rules)", height=200)
        if st.form_submit_button("Save Brand"):
            st.session_state.clients[name] = {"gem_instructions": gem, "voice_dna": ""}
            save_db(st.session_state.clients)
            st.rerun()
    st.divider()
    for b in client_list:
        if st.button(f"Delete {b}"):
            del st.session_state.clients[b]
            save_db(st.session_state.clients)
            st.rerun()

elif not client_list:
    st.warning("⚠️ Add a brand in 'Manage Clients' first to unlock tools!")

# --- TOOL 2: CONTENT FACTORY ---
elif mode == "Content Factory ✍️":
    st.title("Content Factory ✍️")
    selected = st.selectbox("Select Brand:", client_list)
    topic = st.text_area("What are we promoting today?")
    if st.button("Generate Post"):
        sys = f"{st.session_state.clients[selected]['gem_instructions']}\n{st.session_state.clients[selected].get('voice_dna','')}"
        st.write(ask_gemini(f"Write a social post about {topic}", sys))

# --- TOOL 3: 6-MONTH STRATEGY ---
elif mode == "6-Month Strategy Lab 📅":
    st.title("Strategy Lab 📅")
    selected = st.selectbox("Select Brand:", client_list)
    months = st.select_slider("Select Timeline:", options=["1 Month", "2 Months", "3 Months", "6 Months"])
    goal = st.text_input("Main Goal (e.g., Sales, Awareness):")
    if st.button("Generate Roadmap"):
        res = ask_gemini(f"Create a detailed {months} content roadmap for: {goal}", st.session_state.clients[selected]['gem_instructions'])
        st.markdown(res)
        st.download_button("📩 Download PDF", create_pdf(f"{months} Roadmap", res), f"Strategy_{selected}.pdf")

# --- TOOL 4: VOICE CLONE LAB ---
elif mode == "Voice Clone Lab 🎙️":
    st.title("Voice Clone Lab 🎙️")
    selected = st.selectbox("Select Brand:", client_list)
    posts = st.text_area("Paste 3 successful posts here to clone the style:", height=200)
    if st.button("Extract DNA"):
        dna = ask_gemini(f"Analyze the writing style and linguistic DNA of these posts: {posts}", "Expert Linguist")
        st.session_state.clients[selected]['voice_dna'] = dna
        save_db(st.session_state.clients)
        st.success("Style DNA Saved!")
        st.write(dna)

# --- TOOL 5: VIRAL HOOK LAB ---
elif mode == "Viral Hook Lab 🔥":
    st.title("Viral Hook Lab 🔥")
    selected = st.selectbox("Select Brand:", client_list)
    topic = st.text_input("Enter Topic/Product:")
    if st.button("Generate 10 Viral Hooks"):
        res = ask_gemini(f"Generate 10 viral psychology hooks for: {topic}", st.session_state.clients[selected]['gem_instructions'])
        st.write(res)

# --- TOOL 6: BRAND GUARDIAN ---
elif mode == "Brand Guardian 🛡️":
    st.title("Brand Guardian 🛡️")
    selected = st.selectbox("Audit Brand:", client_list)
    img_file = st.file_uploader("Upload Image to Audit", type=["png", "jpg"])
    if st.button("Analyze Image") and img_file:
        res = ask_gemini("Analyze this image for brand consistency.", st.session_state.clients[selected]['gem_instructions'], Image.open(img_file))
        st.info(res)

# --- TOOL 7: STRATEGIC HUB ---
elif mode == "Strategic Hub (SWOT/Comp)":
    st.title("Strategic Hub 🧠")
    selected = st.selectbox("Select Brand:", client_list)
    tab1, tab2 = st.tabs(["Competitor Analysis", "SWOT Analysis"])
    with tab1:
        c_img = st.file_uploader("Competitor Post Screenshot", type=["png", "jpg"])
        if st.button("Analyze Competitor"):
            st.write(ask_gemini("How can we beat this?", st.session_state.clients[selected]['gem_instructions'], Image.open(c_img) if c_img else None))
    with tab2:
        if st.button("Generate SWOT"):
            res = ask_gemini("Generate a full SWOT analysis.", st.session_state.clients[selected]['gem_instructions'])
            st.markdown(res)
            st.download_button("📩 Download PDF", create_pdf("SWOT Report", res), f"SWOT_{selected}.pdf")