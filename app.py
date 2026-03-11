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
            if "429" in str(e): return "⚠️ **AI Busy.** Wait 60s."
            if "403" in str(e): return "❌ **API Key Blocked.** Generate a new key in AI Studio."
            return f"❌ **Error:** {str(e)}"

    # --- 5. SIDEBAR NAVIGATION ---
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
                c_data = st.session_state.clients[selected]
                platform = st.selectbox("Platform:", ["Instagram", "LinkedIn", "Facebook"])
                topic = st.text_area("What are we promoting?")
                up_file = st.file_uploader("Upload Image", type=["jpg", "png"])
                img = Image.open(up_file) if up_file else None
                ab_test = st.checkbox("Generate A/B Test Options?")
                
            if st.button("Generate & Preview", type="primary"):
                with st.spinner("Drafting..."):
                    prompt = f"Write a {platform} post about {topic}."
                    if ab_test: prompt += " Provide 3 versions: Benefit-driven, Story-driven, and Punchy."
                    res = ask_gemini(prompt, c_data['gem_instructions'], img)
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
                prompt = f"Take this topic: '{boring_title}' and generate 10 viral hooks using high-level marketing psychology."
                st.write(ask_gemini(prompt, st.session_state.clients[selected]['gem_instructions']))

    # --- TOOL 3: BRAND GUARDIAN ---
    elif mode == "Brand Guardian 🛡️":
        st.title("Brand Guardian 🛡️")
        if client_list:
            selected = st.selectbox("Check against brand:", client_list)
            check_img = st.file_uploader("Upload Graphic", type=["jpg", "png"])
            if st.button("Run Audit") and check_img:
                st.info(ask_gemini("Audit this image for brand consistency and