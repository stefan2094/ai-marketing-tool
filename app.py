import streamlit as st
import time
from google import genai
from google.genai import types
from PIL import Image
import json
import os
import io

# --- 1. CONFIG & AUTH ---
st.set_page_config(page_title="Pure Agency Command", layout="wide", page_icon="🎨")

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

# AI Text Engine
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

# AI Image Engine (Nano Banana 2)
def generate_image(prompt):
    client = genai.Client(api_key=API_KEY)
    try:
        # Powered by Nano Banana 2
        response = client.models.generate_image(
            model='gemini-3-flash-image',
            prompt=prompt,
            config=types.GenerateImageConfig(output_mime_type='image/png')
        )
        return response.generated_images[0].image_bytes
    except Exception as e:
        st.error(f"🎨 Image Error: {str(e)}")
        return None

# --- 3. NAVIGATION ---
mode = st.sidebar.radio("CHOOSE TOOL:", [
    "Manage Clients & Gems", 
    "Content Factory ✍️", 
    "AI Image Lab 🎨",
    "6-Month Strategy Lab 📅", 
    "Voice Clone Lab 🎙️", 
    "Viral Hook Lab 🔥", 
    "Strategic Hub"
])

clients = list(st.session_state.clients.keys())

# --- 4. TOOL LOGIC ---

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

elif mode == "AI Image Lab 🎨":
    st.title("AI Image Lab (Nano Banana) 🎨")
    sel = st.selectbox("Brand Context:", clients)
    desc = st.text_area("Describe the image you want:")
    if st.button("Generate Image"):
        with st.spinner("Nano Banana is painting..."):
            img_bytes = generate_image(f"Brand style: {st.session_state.clients[sel]['gem_instructions']}. Image: {desc}")
            if img_bytes:
                st.image(img_bytes)
                st.download_button("Download Image", img_bytes, "ai_image.png", "image/png")

elif mode == "Content Factory ✍️":
    st.title("Content Factory ✍️")
    sel = st.selectbox("Brand:", clients)
    topic = st.text_area("Topic:")
    gen_img = st.checkbox("Generate matching image with Nano Banana?")
    if st.button("Generate Post"):
        text_res = ask_gemini(f"Write a post about {topic}", st.session_state.clients[sel]['gem_instructions'])
        st.write(text_res)
        if gen_img:
            with st.spinner("Generating Image..."):
                img_bytes = generate_image(f"Social media graphic for: {topic}. Style: {st.session_state.clients[sel]['gem_instructions']}")
                if img_bytes: st.image(img_bytes)

elif mode == "6-Month Strategy Lab 📅":
    st.title("Strategy Lab 📅")
    sel = st.selectbox("Brand:", clients)
    mo = st.select_slider("Timeline:", ["1 Month", "2 Months", "3 Months", "6 Months"])
    goal = st.text_input("Goal:")
    if st.button("Generate Strategy"):
        st.write(ask_gemini(f"Create a {mo} roadmap for {goal}", st.session_state.clients[sel]['gem_instructions']))

# (Other tools like SWOT and Hooks remain functional)
elif mode == "Viral Hook Lab 🔥":
    st.title("Viral Hook Lab 🔥")
    sel = st.selectbox("Brand:", clients)
    topic = st.text_input("Topic:")
    if st.button("Generate 10 Hooks"):
        st.write(ask_gemini(f"10 hooks for {topic}", st.session_state.clients[sel]['gem_instructions']))

elif mode == "Voice Clone Lab 🎙️":
    st.title("Voice Clone Lab 🎙️")
    sel = st.selectbox("Brand:", clients)
    posts = st.text_area("Paste posts:")
    if st.button("Clone DNA"):
        dna = ask_gemini(f"Clone DNA from: {posts}", "Linguist")
        st.session_state.clients[sel]['voice_dna'] = dna
        save_db(st.session_state.clients); st.success("Saved!")

elif mode == "Strategic Hub":
    st.title("Strategic Hub 🧠")
    sel = st.selectbox("Brand:", clients)
    if st.button("Run SWOT"):
        st.write(ask_gemini("Full SWOT analysis.", st.session_state.clients[sel]['gem_instructions']))