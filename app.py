import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Pure Agency Command", layout="wide")

# --- LOGIN GATE ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 Agency Command Center")
        pwd = st.text_input("Enter Access Code:", type="password")
        if st.button("Unlock Tools"):
            if pwd == st.secrets["AGENCY_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Incorrect Code")
        return False
    return True

if check_password():
    # --- DB & API ---
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
            if "403" in str(e): return "❌ **API Key Blocked.** Please generate a new key in AI Studio and update Streamlit Secrets."
            return f"❌ **Error:** {str(e)}"

    # --- SIDEBAR & TOOLS ---
    st.sidebar.title("🚀 Elite Command")
    mode = st.sidebar.radio("Tool:", ["Content Factory", "Viral Hook Lab 🔥", "Manage Clients"])
    client_list = list(st.session_state.clients.keys())

    if mode == "Content Factory":
        st.title("Content Factory ✍️")
        if not client_list: st.warning("Add a brand first!")
        else:
            selected = st.selectbox("Select Brand:", client_list)
            topic = st.text_area("What are we promoting?")
            up_file = st.file_uploader("Image", type=["jpg", "png"])
            if st.button("Generate"):
                res = ask_gemini(f"Write a post about {topic}", st.session_state.clients[selected]['gem_instructions'], Image.open(up_file) if up_file else None)
                st.write(res)

    elif mode == "Viral Hook Lab 🔥":
        st.title("Viral Hook Lab 🔥")
        topic = st.text_input("Boring headline:")
        if st.button("Generate Hooks") and client_list:
            st.write(ask_gemini(f"Viral hooks for: {topic}", st.session_state.clients[client_list[0]]['gem_instructions']))

    elif mode == "Manage Clients":
        st.title("Manage Clients 👤")
        with st.form("add_client"):
            name = st.text_input("Brand Name")
            gem = st.text_area("Gem Instructions", height=200)
            if st.form_submit_button("Save"):
                st.session_state.clients[name] = {"gem_instructions": gem}
                save_db(st.session_state.clients)
                st.rerun()
        for b in list(st.session_state.clients.keys()):
            if st.button(f"Delete {b}"):
                del st.session_state.clients[b]
                save_db(st.session_state.clients)
                st.rerun()