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
        st.success("📥 MeisterTask Request Received")
        mt_topic = query_params["task_topic"]
        mt_brand = query_params.get("brand", "Default")
        mt_date = query_params.get("due_date", "Not Set") # Grab the date from MeisterTask
        
        if mt_brand in st.session_state.clients:
            st.subheader(f"Auto-Drafting for: {mt_brand}")
            c_data = st.session_state.clients[mt_brand]
            sys_inst = f"{c_data.get('gem_instructions','')}\n{c_data.get('voice_dna','')}"
            
            with st.spinner("AI is crafting the post..."):
                draft = ask_gemini(f"Create a social media post for this task: {mt_topic}", sys_inst)
                st.info(f"📅 Scheduled Date: {mt_date}")
                st.write(draft)
                
                # NEW: Button to manually confirm the schedule to SocialPilot
                if st.button("🚀 Confirm & Schedule to SocialPilot"):
                    st.success("Successfully pushed to SocialPilot!")
                    # Note: The actual "Push" happens in the Make.com step 4.
        else:
            st.error(f"Brand '{mt_brand}' not found.")
        st.divider()

    # --- 6. SIDEBAR NAVIGATION ---
    st.sidebar.title("🚀 Elite Command")
    mode = st.sidebar.radio("CHOOSE TOOL:", [
        "Content & Mockup Factory", 
        "Voice Clone Lab 🎙️",
        "Viral Hook Lab 🔥", 
        "Brand Guardian 🛡️",
        "Strategic Hub (SWOT/Comp)", 
        "Manage Clients & Gems"
    ])

    client_list = list(st.session_state.clients.keys())

    # --- TOOL 1: CONTENT & MOCKUP FACTORY ---
    if mode == "Content & Mockup Factory":
        st.title("Content & Mockup Factory ✍️📱")
        if not client_list: st.warning("Add a brand first!")
        else:
            col1, col2 = st.columns([1, 1])
            with col1:
                selected = st.selectbox("Select Brand:", client_list)
                c_data = st.session_state.clients[selected]
                platform = st.selectbox("Platform:", ["Instagram", "LinkedIn", "Facebook"])
                topic = st.text_area("What are we promoting?")
                up_file = st.file_uploader("Upload Image", type=["jpg", "png"])
                img = Image.open(up_file) if up_file else None
                
            if st.button("Generate & Preview", type="primary"):
                sys_inst = f"{c_data.get('gem_instructions','')}\n{c_data.get('voice_dna','')}"
                res = ask_gemini(f"Write a {platform} post about {topic}.", sys_inst, img)
                with col2:
                    st.subheader(f"{platform} Preview")
                    with st.container(border=True):
                        st.markdown(f"**@{selected.replace(' ', '').lower()}**")
                        if img: st.image(img, use_container_width=True)
                        st.write(res)

    # --- TOOL 2: VOICE CLONE LAB ---
    elif mode == "Voice Clone Lab 🎙️":
        st.title("Voice Clone Lab 🎙️")
        if client_list:
            selected = st.selectbox("Cloning Voice for:", client_list)
            past_posts = st.text_area("Paste 3 successful posts here:", height=300)
            if st.button("Analyze & Clone DNA"):
                dna = ask_gemini(f"Analyze writing style: {past_posts}", "Linguistic Expert")
                st.session_state.clients[selected]['voice_dna'] = dna
                save_db(st.session_state.clients)
                st.success("DNA Saved!")
                st.write(dna)

    # --- TOOL 3: MANAGE CLIENTS ---
    elif mode == "Manage Clients & Gems":
        st.title("Manage Clients 👤💎")
        with st.form("client_form"):
            name = st.text_input("Brand Name")
            gem = st.text_area("Gem Instructions", height=250)
            if st.form_submit_button("Save Brand"):
                st.session_state.clients[name] = {"gem_instructions": gem, "voice_dna": ""}
                save_db(st.session_state.clients)
                st.rerun()
        st.divider()
        for b_name in list(st.session_state.clients.keys()):
            if st.button(f"Delete {b_name}"):
                del st.session_state.clients[b_name]
                save_db(st.session_state.clients)
                st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()