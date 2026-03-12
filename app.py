import streamlit as st
import time
from google import genai
from google.genai import types
from PIL import Image
import json
import os
from fpdf import FPDF

# --- 1. CONFIG & AUTH ---
st.set_page_config(page_title="Pure Agency Command", layout="wide")

if "password_correct" not in st.session_state:
    st.title("🔐 Agency Command Center")
    pwd = st.text_input("Access Code:", type="password")
    if st.button("Unlock"):
        if pwd == st.secrets["AGENCY_PASSWORD"]:
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("❌ Denied")
    st.stop()

# --- 2. DATABASE & AI ENGINE ---
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

def ask_gemini(prompt, sys_inst, image=None):
    client = genai.Client(api_key=API_KEY)
    contents = [prompt]
    if image: contents.append(image)
    for attempt in range(3):
        try:
            return client.models.generate_content(
                model='gemini-3-flash-preview', 
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=sys_inst)
            ).text
        except Exception as e:
            if "429" in str(e): time.sleep(3); continue
            return f"❌ Error: {str(e)}"

# --- 3. AUTOMATION LISTENER (MeisterTask Bridge) ---
q = st.query_params
if "task_topic" in q:
    st.info(f"🤖 Automation Active: {q['task_topic']}")
    if q.get("brand") in st.session_state.clients:
        brand_data = st.session_state.clients[q["brand"]]
        if st.button("🚀 Draft & Push to SocialPilot"):
            res = ask_gemini(f"Draft social post for: {q['task_topic']}", brand_data['gem_instructions'])
            st.code(res)
    st.divider()

# --- 4. NAVIGATION & TOOLS ---
mode = st.sidebar.radio("CHOOSE TOOL:", [
    "Manage Clients & Gems", "Content Factory ✍️", "6-Month Strategy Lab 📅", 
    "Voice Clone Lab 🎙️", "Viral Hook Lab 🔥", "Brand Guardian 🛡️", "Strategic Hub"
])

clients = list(st.session_state.clients.keys())

if mode == "Manage Clients & Gems":
    st.title("Manage Clients 👤")
    with st.form("add"):
        name = st.text_input("Brand Name")
        gem = st.text_area("Instructions", height=200)
        if st.form_submit_button("Save"):
            st.session_state.clients[name] = {"gem_instructions": gem, "voice_dna": ""}
            save_db(st.session_state.clients); st.rerun()
    for b in clients:
        if st.button(f"Delete {b}"):
            del st.session_state.clients[b]; save_db(st.session_state.clients); st.rerun()

elif not clients: st.warning("Add a brand first!")

elif mode == "6-Month Strategy Lab 📅":
    st.title("Strategy Lab 📅")
    sel = st.selectbox("Brand:", clients)
    mo = st.select_slider("Timeline:", ["1 Month", "2 Months", "3 Months", "6 Months"])
    goal = st.text_input("Goal:")
    if st.button("Generate Strategy"):
        st.write(ask_gemini(f"Create a {mo} roadmap for {goal}", st.session_state.clients[sel]['gem_instructions']))

elif mode == "Content Factory ✍️":
    st.title("Content Factory ✍️")
    sel = st.selectbox("Brand:", clients)
    topic = st.text_area("Topic:")
    if st.button("Generate"):
        st.write(ask_gemini(f"Write a post about {topic}", st.session_state.clients[sel]['gem_instructions']))

elif mode == "Voice Clone Lab 🎙️":
    st.title("Voice Clone Lab 🎙️")
    sel = st.selectbox("Brand:", clients)
    posts = st.text_area("Paste posts:")
    if st.button("Clone DNA"):
        dna = ask_gemini(f"Clone DNA from: {posts}", "Linguist")
        st.session_state.clients[sel]['voice_dna'] = dna
        save_db(st.session_state.clients); st.success("Saved!")

elif mode == "Viral Hook Lab 🔥":
    st.title("Viral Hook Lab 🔥")
    sel = st.selectbox("Brand:", clients)
    topic = st.text_input("Topic:")
    if st.button("Generate 10 Hooks"):
        st.write(ask_gemini(f"10 hooks for {topic}", st.session_state.clients[sel]['gem_instructions']))

elif mode == "Brand Guardian 🛡️":
    st.title("Brand Guardian 🛡️")
    sel = st.selectbox("Brand:", clients)
    img = st.file_uploader("Upload Image", type=["png", "jpg"])
    if st.button("Audit") and img:
        st.write(ask_gemini("Audit this image.", st.session_state.clients[sel]['gem_instructions'], Image.open(img)))

elif mode == "Strategic Hub":
    st.title("Strategic Hub 🧠")
    sel = st.selectbox("Brand:", clients)
    if st.button("Run SWOT"):
        st.write(ask_gemini("Full SWOT analysis.", st.session_state.clients[sel]['gem_instructions']))