import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import os
import time

# --- 1. PRO SETTINGS & UI STYLING ---
st.set_page_config(page_title="MARKT-AI Command Center", page_icon="📈", layout="wide")

# Professional SaaS Styling
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1E1E1E; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #333333; border: 1px solid #00D1FF; }
    .stExpander { border: 1px solid #DFE1E5; border-radius: 8px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PERMANENT DATABASE & SECRETS ---
# Use the secret we set up on Streamlit Cloud
API_KEY = st.secrets["GEMINI_API_KEY"]
DB_FILE = "client_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

if "clients" not in st.session_state:
    st.session_state.clients = load_db()

# --- 3. THE LIVE-STREAMING ENGINE ---
def stream_gemini(prompt, system_instruction, image=None):
    client = genai.Client(api_key=API_KEY)
    contents = [prompt]
    if image:
        contents.append(image)
    
    # Generate content as a stream for the "typing" effect
    responses = client.models.generate_content_stream(
        model='gemini-2.0-flash',
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system_instruction)
    )
    for chunk in responses:
        yield chunk.text

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛡️ MARKT-AI PRO")
    st.caption("Agency Command Center v3.0")
    st.markdown("---")
    mode = st.radio("WORKSPACES", [
        "Content Factory", 
        "Campaign Architect 🏛️", 
        "Brand Guardian & Audit 🛡️",
        "Viral Hook Lab 🔥",
        "Manage Clients & Brand Kits"
    ])
    st.markdown("---")
    st.success("System: Online")

client_list = list(st.session_state.clients.keys())

# ==========================================
# TOOL 1: CONTENT FACTORY (With Mockup & Streaming)
# ==========================================
if mode == "Content Factory":
    st.title("Content Factory ✍️")
    if not client_list: st.warning("Add a client in settings first!")
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            selected = st.selectbox("Select Client", client_list)
            c_data = st.session_state.clients[selected]
            platform = st.selectbox("Platform", ["Instagram", "LinkedIn", "Facebook", "TikTok"])
            topic = st.text_area("Promotion Details", placeholder="What are we announcing?")
            up_file = st.file_uploader("Visual Reference", type=["jpg", "png"])
            img = Image.open(up_file) if up_file else None

        if st.button("Generate & Stream Draft"):
            with col2:
                st.subheader(f"Live {platform} Preview")
                with st.container(border=True):
                    st.caption(f"Drafting for {selected}...")
                    # This creates the professional word-by-word typing effect
                    st.write_stream(stream_gemini(f"Write a {platform} post about: {topic}.", c_data['gem_instructions'], img))

# ==========================================
# TOOL 2: CAMPAIGN ARCHITECT (THE BIG UPGRADE)
# ==========================================
elif mode == "Campaign Architect 🏛️":
    st.title("Campaign Architect 🏛️")
    st.write("Turn one idea into a full-scale multi-channel marketing assault.")
    
    if client_list:
        selected = st.selectbox("Client", client_list)
        c_data = st.session_state.clients[selected]
        concept = st.text_input("The Big Concept", placeholder="e.g., Summer Blowout Sale or New Product Launch")
        channels = st.multiselect("Active Channels", ["Email Sequence", "Meta Ads", "LinkedIn Thought Leadership", "TikTok Scripts"], default=["Email Sequence", "Meta Ads"])
        
        if st.button("Architect Campaign"):
            st.divider()
            full_prompt = f"Create a cohesive campaign for '{concept}'. Channels requested: {', '.join(channels)}. For each channel, provide high-converting copy and the strategic 'why' behind it."
            st.write_stream(stream_gemini(full_prompt, c_data['gem_instructions']))

# ==========================================
# TOOL 3: BRAND GUARDIAN (Audit Tool)
# ==========================================
elif mode == "Brand Guardian & Audit 🛡️":
    st.title("Brand Guardian 🛡️")
    selected = st.selectbox("Client", client_list)
    c_data = st.session_state.clients[selected]
    
    st.write("Upload a final creative or caption to check it against the client's Brand Kit.")
    check_type = st.radio("Check Type", ["Text Audit", "Visual Audit"])
    
    if check_type == "Text Audit":
        text_to_check = st.text_area("Paste caption to audit:")
        if st.button("Run Text Audit"):
            st.write_stream(stream_gemini(f"Audit this text against the brand's voice. Identify if it sounds off-brand and provide 3 corrections: {text_to_check}", c_data['gem_instructions']))
    else:
        v_file = st.file_uploader("Upload Image", type=["jpg", "png"])
        if st.button("Run Visual Audit"):
            if v_file:
                st.write_stream(stream_gemini("Check this image against our brand voice. Is the vibe correct? Is it too cluttered? Does it align with our audience?", c_data['gem_instructions'], Image.open(v_file)))

# ==========================================
# TOOL 4: VIRAL HOOK LAB
# ==========================================
elif mode == "Viral Hook Lab 🔥":
    st.title("Viral Hook Lab 🔥")
    selected = st.selectbox("Client", client_list)
    topic = st.text_input("Topic to Hook:")
    if st.button("Generate 10 Hooks"):
        st.write_stream(stream_gemini(f"Generate 10 viral hooks for: {topic}. Use patterns like 'The Secret of', 'Stop doing X', and 'How I achieved Y'.", st.session_state.clients[selected]['gem_instructions']))

# ==========================================
# TOOL 5: MANAGE CLIENTS & BRAND KITS
# ==========================================
elif mode == "Manage Clients & Brand Kits":
    st.title("Client Command 👤💎")
    
    with st.form("new_client"):
        name = st.text_input("Brand Name")
        voice = st.text_input("Brand Voice (e.g., Luxury, Bold, Scientific)")
        guidelines = st.text_area("Master Brand Kit (Gem Instructions)", height=300, placeholder="Paste the unique rules, audience data, and persona here...")
        if st.form_submit_button("Save Brand Profile"):
            if name and guidelines:
                st.session_state.clients[name] = {"voice": voice, "gem_instructions": guidelines}
                save_db(st.session_state.clients)
                st.success(f"{name} Profile Secured!")
                st.rerun()

    st.divider()
    for b in client_list:
        with st.expander(f"⚙️ Manage {b}"):
            st.write(f"**Current Voice:** {st.session_state.clients[b]['voice']}")
            if st.button(f"Permanently Delete {b}", key=f"del_{b}"):
                del st.session_state.clients[b]
                save_db(st.session_state.clients)
                st.rerun()