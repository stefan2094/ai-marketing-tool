import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import os

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

    # --- 5. SIDEBAR NAVIGATION (All 5 Tools) ---
    st.sidebar.title("🚀 Elite Command")
    mode = st.sidebar.radio("CHOOSE TOOL:", [
        "Content & Mockup Factory", 
        "Viral Hook Lab 🔥", 
        "Brand Guardian 🛡️",
        "Strategic Hub (SWOT/Comp)", 
        "Manage Clients & Gems"
    ])

    client_list = list(st.session_state.clients.keys())

    # --- TOOL 1: CONTENT & MOCKUP ---
    if mode == "Content & Mockup Factory":
        st.title("Content & Mockup Factory ✍️📱")
        if not client_list: st.warning("Add a brand in 'Manage Clients' first!")
        else:
            col1, col2 = st.columns([1, 1])
            with col1:
                selected = st.selectbox("Select Brand:", client_list)
                platform = st.selectbox("Platform:", ["Instagram", "LinkedIn", "Facebook"])
                topic = st.text_area("What are we promoting?")
                up_file = st.file_uploader("Upload Image", type=["jpg", "png"])
                img = Image.open(up_file) if up_file else None
                ab_test = st.checkbox("Generate A/B Test Options?")
                
            if st.button("Generate & Preview", type="primary"):
                with st.spinner("Drafting..."):
                    prompt = f"Write a {platform} post about {topic}."
                    if ab_test: prompt += " Provide 3 versions: Benefit-driven, Story-driven, and Punchy."
                    res = ask_gemini(prompt, st.session_state.clients[selected]['gem_instructions'], img)
                    with col2:
                        st.subheader(f"{platform} Preview")
                        with st.container(border=True):
                            st.markdown(f"**@{selected.replace(' ', '').lower()}**")
                            if img: st.image(img, use_container_width=True)
                            st.write(res)
                            st.caption("❤️ 💬 🚀 Liked by AI and 1,240 others")

    # --- TOOL 2: VIRAL HOOK LAB ---
    elif mode == "Viral Hook Lab 🔥":
        st.title("Viral Hook Lab 🔥")
        if not client_list: st.warning("Add a brand first!")
        else:
            selected = st.selectbox("Brand Context:", client_list)
            boring_title = st.text_input("Enter your 'boring' headline:")
            if st.button("Generate 10 Viral Hooks"):
                st.write(ask_gemini(f"Generate 10 viral hooks for: {boring_title}", st.session_state.clients[selected]['gem_instructions']))

    # --- TOOL 3: BRAND GUARDIAN ---
    elif mode == "Brand Guardian 🛡️":
        st.title("Brand Guardian 🛡️")
        if client_list:
            selected = st.selectbox("Check against brand:", client_list)
            check_img = st.file_uploader("Upload Graphic", type=["jpg", "png"])
            if st.button("Run Audit") and check_img:
                st.info(ask_gemini("Audit this image for brand consistency.", st.session_state.clients[selected]['gem_instructions'], Image.open(check_img)))

    # --- TOOL 4: STRATEGIC HUB ---
    elif mode == "Strategic Hub (SWOT/Comp)":
        st.title("Strategic Analysis 🧠")
        if client_list:
            selected = st.selectbox("Select Brand:", client_list)
            t1, t2 = st.tabs(["Competitor Analysis", "SWOT"])
            with t1:
                comp_img = st.file_uploader("Competitor Image", type=["jpg", "png"])
                if st.button("Analyze"):
                    st.write(ask_gemini("How can we beat this competitor?", st.session_state.clients[selected]['gem_instructions'], Image.open(comp_img) if comp_img else None))
            with t2:
                if st.button("Generate SWOT"):
                    st.markdown(ask_gemini("Generate a full SWOT analysis.", st.session_state.clients[selected]['gem_instructions']))

    # --- TOOL 5: MANAGE CLIENTS ---
    elif mode == "Manage Clients & Gems":
        st.title("Manage Clients 👤💎")
        with st.form("client_form"):
            name = st.text_input("Brand Name")
            gem = st.text_area("Paste Custom Gem Instructions", height=250)
            if st.form_submit_button("Save Brand"):
                st.session_state.clients[name] = {"gem_instructions": gem}
                save_db(st.session_state.clients)
                st.success(f"Saved {name}!")
                st.rerun()
        for b_name in list(st.session_state.clients.keys()):
            if st.button(f"Delete {b_name}"):
                del st.session_state.clients[b_name]
                save_db(st.session_state.clients)
                st.rerun()