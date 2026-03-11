import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import os

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
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

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

# --- 5. SIDEBAR NAVIGATION ---
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

# --- TOOL: MANAGE CLIENTS (Always visible) ---
if mode == "Manage Clients & Gems":
    st.title("Manage Clients 👤💎")
    st.write("Add your brands here first to unlock other tools.")
    with st.form("client_form"):
        name = st.text_input("Brand Name")
        gem = st.text_area("Base Gem Instructions (Tone, Target Audience, Rules)", height=250)
        if st.form_submit_button("Save Brand"):
            if name:
                st.session_state.clients[name] = {"gem_instructions": gem, "voice_dna": ""}
                save_db(st.session_state.clients)
                st.success(f"Saved {name}!")
                st.rerun()
            else:
                st.error("Please enter a Brand Name.")
    
    st.divider()
    st.subheader("Current Brands")
    for b_name in client_list:
        col1, col2 = st.columns([4, 1])
        col1.write(f"🏷️ {b_name}")
        if col2.button("Delete", key=f"del_{b_name}"):
            del st.session_state.clients[b_name]
            save_db(st.session_state.clients)
            st.rerun()

# --- OTHER TOOLS (Only show if clients exist) ---
elif not client_list:
    st.warning("⚠️ No brands found. Go to 'Manage Clients & Gems' to add one first!")

elif mode == "Strategic Hub (SWOT/Comp)":
    st.title("Strategic Analysis Hub 🧠")
    selected = st.selectbox("Select Client:", client_list)
    t1, t2 = st.tabs(["Competitor Analysis", "SWOT Analysis"])
    sys_inst = st.session_state.clients[selected]['gem_instructions']
    with t1:
        comp_img = st.file_uploader("Upload Competitor Screenshot", type=["jpg", "png"])
        if st.button("Analyze Competitor"):
            st.write(ask_gemini("How can we beat this competitor?", sys_inst, Image.open(comp_img) if comp_img else None))
    with t2:
        if st.button("Generate Full SWOT"):
            st.markdown(ask_gemini("Generate a full SWOT analysis for this brand.", sys_inst))

elif mode == "Viral Hook Lab 🔥":
    st.title("Viral Hook Lab 🔥")
    selected = st.selectbox("Brand Context:", client_list)
    topic = st.text_input("Enter your topic/headline:")
    if st.button("Generate 10 Viral Hooks"):
        sys_inst = st.session_state.clients[selected]['gem_instructions']
        st.write(ask_gemini(f"Generate 10 viral hooks for: {topic}", sys_inst))

elif mode == "Brand Guardian 🛡️":
    st.title("Brand Guardian 🛡️")
    selected = st.selectbox("Audit against Brand:", client_list)
    check_img = st.file_uploader("Upload Graphic for Audit", type=["jpg", "png"])
    if st.button("Run Brand Audit") and check_img:
        sys_inst = st.session_state.clients[selected]['gem_instructions']
        st.info(ask_gemini("Audit this content for brand consistency.", sys_inst, Image.open(check_img)))

elif mode == "Content & Mockup Factory":
    st.title("Content & Mockup Factory ✍️📱")
    selected = st.selectbox("Select Brand:", client_list)
    c_data = st.session_state.clients[selected]
    topic = st.text_area("What are we promoting?")
    if st.button("Generate"):
        sys_inst = f"{c_data.get('gem_instructions','')}\n{c_data.get('voice_dna','')}"
        st.write(ask_gemini(f"Write a social post about {topic}.", sys_inst))

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()