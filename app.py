import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import os
import requests

# --- 1. PRO APP CONFIG ---
st.set_page_config(page_title="Pure Agency Command", layout="wide", initial_sidebar_state="expanded")

# --- 2. THE LOGIN GATE ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 Agency Command Center")
        pwd = st.text_input("Enter Agency Access Code:", type="password")
        if st.button("Unlock Command Center"):
            if pwd == st.secrets["AGENCY_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Access Denied")
        return False
    return True

if check_password():
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

    # --- 5. MEISTERTASK & SOCIALPILOT HANDLER ---
    query_params = st.query_params
    if "task_topic" in query_params:
        st.success("📥 Incoming Automation Task")
        mt_topic = query_params["task_topic"]
        mt_brand = query_params.get("brand", "Default")
        mt_date = query_params.get("due_date", "") 
        
        if mt_brand in st.session_state.clients:
            c_data = st.session_state.clients[mt_brand]
            sys_inst = f"{c_data.get('gem_instructions','')}\n{c_data.get('voice_dna','')}"
            
            with st.spinner("AI is generating your scheduled post..."):
                draft = ask_gemini(f"Write a social media post: {mt_topic}", sys_inst)
                st.info(f"📅 Intended Date: {mt_date}")
                st.write(draft)
                # This draft is now what Make.com will pick up
                st.session_state['last_ai_draft'] = draft
        else:
            st.error(f"Brand '{mt_brand}' not found.")

    # --- 6. SIDEBAR NAVIGATION ---
    st.sidebar.title("🚀 Elite Command")
    mode = st.sidebar.radio("CHOOSE TOOL:", ["Content Factory", "Voice Clone Lab 🎙️", "Manage Clients"])

    client_list = list(st.session_state.clients.keys())

    if mode == "Content Factory":
        st.title("Content Factory ✍️")
        if client_list:
            selected = st.selectbox("Select Brand:", client_list)
            topic = st.text_area("What are we promoting?")
            if st.button("Generate"):
                res = ask_gemini(topic, st.session_state.clients[selected]['gem_instructions'])
                st.write(res)

    elif mode == "Voice Clone Lab 🎙️":
        st.title("Voice Clone Lab 🎙️")
        selected = st.selectbox("Brand:", client_list)
        past_posts = st.text_area("Paste 3 successful posts:")
        if st.button("Clone DNA"):
            dna = ask_gemini(f"Analyze style: {past_posts}", "Linguist")
            st.session_state.clients[selected]['voice_dna'] = dna
            save_db(st.session_state.clients)
            st.success("DNA Saved!")

    elif mode == "Manage Clients":
        st.title("Manage Clients 👤")
        with st.form("add"):
            name = st.text_input("Brand Name")
            gem = st.text_area("Instructions")
            if st.form_submit_button("Save"):
                st.session_state.clients[name] = {"gem_instructions": gem, "voice_dna": ""}
                save_db(st.session_state.clients)
                st.rerun()