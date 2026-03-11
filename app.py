import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import os

# --- 1. PRO APP CONFIG ---
st.set_page_config(page_title="Elite Marketing Command", layout="wide", initial_sidebar_state="expanded")

# --- 2. YOUR API KEY ---
API_KEY = "AIzaSyBIHXZdplRKdfOFP4YaS2LVsBXTWRwe1ro"

# --- 3. PERMANENT DATABASE LOGIC ---
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
    if API_KEY == "PASTE_YOUR_API_KEY_HERE":
        return "❌ Add API Key to line 13!"
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
        if "429" in str(e): return "⚠️ **AI Busy (Quota).** Wait 60s and retry."
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

# ==========================================
# TOOL 1: CONTENT & MOCKUP FACTORY
# ==========================================
if mode == "Content & Mockup Factory":
    st.title("Content & Mockup Factory ✍️📱")
    if not client_list: st.warning("Add a client first!")
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            selected = st.selectbox("Select Brand:", client_list)
            c_data = st.session_state.clients[selected]
            platform = st.selectbox("Platform:", ["Instagram", "LinkedIn", "Facebook"])
            topic = st.text_area("Topic:")
            uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png"])
            img = Image.open(uploaded_file) if uploaded_file else None
            
        if st.button("Generate & Preview", type="primary"):
            with st.spinner("Writing..."):
                res = ask_gemini(f"Write a {platform} post about {topic}.", c_data['gem_instructions'], img)
                with col2:
                    st.subheader(f"{platform} Mockup")
                    # This creates a "phone screen" look
                    with st.container(border=True):
                        st.markdown(f"**@{selected.replace(' ', '').lower()}**")
                        if img: st.image(img, use_container_width=True)
                        st.write(res)
                        st.caption("❤️ 💬 🚀 Liked by AI and 1,240 others")

# ==========================================
# TOOL 2: VIRAL HOOK LAB
# ==========================================
elif mode == "Viral Hook Lab 🔥":
    st.title("Viral Hook Lab 🔥")
    if not client_list: st.warning("Add a client first!")
    else:
        selected = st.selectbox("Brand Context:", client_list)
        c_data = st.session_state.clients[selected]
        boring_title = st.text_input("Enter your 'boring' headline or topic:")
        
        if st.button("Generate 10 Viral Hooks"):
            with st.spinner("Analyzing trends..."):
                prompt = f"Take this boring topic: '{boring_title}' and generate 10 high-performance hooks. Use psychology: FOMO, curiosity, negative constraints, and data-backed authority."
                hooks = ask_gemini(prompt, c_data['gem_instructions'])
                st.success("Hooks Generated!")
                st.write(hooks)

# ==========================================
# TOOL 3: BRAND GUARDIAN
# ==========================================
elif mode == "Brand Guardian 🛡️":
    st.title("Brand Guardian 🛡️")
    if not client_list: st.warning("Add a client first!")
    else:
        selected = st.selectbox("Select Brand Guidelines:", client_list)
        c_data = st.session_state.clients[selected]
        
        st.write("Upload a graphic to check it against brand rules.")
        check_img = st.file_uploader("Upload Creative", type=["jpg", "png"])
        guidelines = st.text_area("Specific Rules to check (Optional):", placeholder="e.g., Logo must be in top right. No neon colors.")
        
        if st.button("Run Brand Audit"):
            if check_img:
                with st.spinner("Auditing creative..."):
                    prompt = f"Audit this image against the brand's voice and these rules: {guidelines}. Does it look professional? Is the logo placement okay? Point out any violations."
                    audit = ask_gemini(prompt, c_data['gem_instructions'], Image.open(check_img))
                    st.info(audit)
            else: st.warning("Please upload an image to audit.")

# ==========================================
# STRATEGIC HUB (SWOT/COMP)
# ==========================================
elif mode == "Strategic Hub (SWOT/Comp)":
    st.title("Strategic Analysis 🧠")
    if client_list:
        selected = st.selectbox("Select Brand:", client_list)
        c_data = st.session_state.clients[selected]
        t1, t2 = st.tabs(["Competitor Analysis", "SWOT"])
        with t1:
            comp_img = st.file_uploader("Competitor Image", type=["jpg", "png"])
            if st.button("Analyze"):
                res = ask_gemini("Analyze this competitor and tell me how to beat them.", c_data['gem_instructions'], Image.open(comp_img) if comp_img else None)
                st.write(res)
        with t2:
            if st.button("Generate SWOT"):
                st.write(ask_gemini("Generate a full SWOT analysis.", c_data['gem_instructions']))

# ==========================================
# MANAGE CLIENTS & GEMS
# ==========================================
elif mode == "Manage Clients & Gems":
    st.title("Manage Clients 👤💎")
    with st.form("client_form"):
        name = st.text_input("Brand Name")
        gem = st.text_area("Paste Client Gem Instructions (The Brain)", height=250)
        if st.form_submit_button("Save"):
            if name and gem:
                st.session_state.clients[name] = {"gem_instructions": gem}
                save_db(st.session_state.clients)
                st.success(f"Saved {name}!")
                st.rerun()
    st.divider()
    for b_name in list(st.session_state.clients.keys()):
        c1, c2 = st.columns([4, 1])
        c1.write(f"🏷️ **{b_name}**")
        if c2.button("Delete", key=f"del_{b_name}"):
            del st.session_state.clients[b_name]
            save_db(st.session_state.clients)
            st.rerun()