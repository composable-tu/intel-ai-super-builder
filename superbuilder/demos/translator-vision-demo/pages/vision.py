import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'example', 'python')))
import sthelpers.stream_utils as sthelpers

import streamlit as st
import json
import time
import grpc

# Add example/python to sys.path for imports (adjust path as needed)
import helpers.config as config
import helpers.model as model
import helpers.chat as chat
import tempfile
import shutil

# Add the project root to sys.path so "helpers" can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

success = False
stub = None
channel = None
active_model = None

ACTION_BUTTON_NAME='Run Analysis'
DEFAULT_PROMPT = "Summarize the image"
DEFAULT_RECEIPT_SCAN_PROMPT = "Review the receipt image and extract transaction details. Provide the information in a nice format."
DEFAULT_IMG_LABEL_PROMPT = "Review the image and assign up to 3 category labels to it"

ST_LOADING_HTML = sthelpers.get_loading_gif()


if 'vlm_loaded' not in st.session_state:
    st.session_state.vlm_loaded = False
if 'vlm_loading' not in st.session_state:
    st.session_state.vlm_loading = False

st.title("Vision Demo (gRPC VLM)")

# --- Ping SuperBuilder Service ---
st.markdown("<h3 class='dual-title'>Check AI Assistant Builder Service <span>(gRPC VLM)</span></h3>", unsafe_allow_html=True)
vision_ping_col1, vision_ping_col2 = st.columns([1, 3])
with vision_ping_col1:
    vision_ping_clicked = st.button("Ping Local LLM Service", key="ping_vision_model")

if vision_ping_clicked:
    try:
        if not stub:
            success, stub, channel = sthelpers.aab_connect()        
        if not success:
            st.session_state["vision_ping_result"] = json.dumps({"error": "Failed to connect to gRPC backend"}, ensure_ascii=False, indent=2)
            st.stop()
        else:
            st.session_state["vision_ping_result"] = "Vision model service connected"
        resp = config.get_config(stub)
        pretty_json = json.dumps(resp, ensure_ascii=False, indent=2)
        st.session_state["vision_ping_result"] = pretty_json
    except Exception as e:
        st.session_state["vision_ping_result"] = json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)

with vision_ping_col2:
    vision_ping_result = st.session_state.get("vision_ping_result", "")
    st.markdown("""
    <style>
    div[data-testid="stCodeBlock"] {
        border: 1.5px solid #bbb !important;
        border-radius: 6px !important;
        background: #f8f8f8 !important;
        height: 200px !important;
        max-height: 200px !important;
        overflow: auto !important;
        box-sizing: border-box;
    }
    </style>
    """, unsafe_allow_html=True)
    st.code(vision_ping_result, language="json", height=300)

# --- File Selection (Image) ---
st.markdown("<h3 class='dual-title'>Vision File Selection</h3>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Select an image file", type=["png", "jpg", "jpeg"])
attachedFiles=[]

# Clear output when a new image is loaded
if "last_uploaded_filename" not in st.session_state:
    st.session_state["last_uploaded_filename"] = None

if uploaded_file is not None:
    if uploaded_file.name != st.session_state["last_uploaded_filename"]:
        st.session_state["vision_result"] = None
        st.session_state["run_vision"] = False
        st.session_state["last_uploaded_filename"] = uploaded_file.name

# --- Two Panel Layout ---
if uploaded_file:
    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp_file:
        shutil.copyfileobj(uploaded_file, tmp_file)
        tmp_file_path = tmp_file.name
    attachedFiles = [tmp_file_path]

    col1, col2 = st.columns([1, 1])
    with col1:
        # Limit image preview to max height 300px
        st.markdown(
            """
            <style>
            .vision-img-preview img {
                max-height: 300px !important;
                width: auto !important;
                display: block;
                margin-left: auto;
                margin-right: auto;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="vision-img-preview">', unsafe_allow_html=True)
        st.image(uploaded_file, caption="Preview", use_container_width=False)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- New Quick Action Buttons (inline) ---
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            scan_receipt_clicked = st.button("Scan Receipt", use_container_width=True)
        with btn_col2:
            label_image_clicked = st.button("Label Image", use_container_width=True)

        # --- Handle quick action logic BEFORE text_area is created ---
        if scan_receipt_clicked:
            st.session_state["vision_prompt"] = DEFAULT_RECEIPT_SCAN_PROMPT
            st.session_state["vision_prompt_input"] = DEFAULT_RECEIPT_SCAN_PROMPT
            st.session_state.vision_result = None
            st.session_state.run_vision = True
            if not st.session_state.get('vlm_loaded', False):
                st.session_state.vlm_loading = True
            st.rerun()
        elif label_image_clicked:
            st.session_state["vision_prompt"] = DEFAULT_IMG_LABEL_PROMPT
            st.session_state["vision_prompt_input"] = DEFAULT_IMG_LABEL_PROMPT
            st.session_state.vision_result = None
            st.session_state.run_vision = True
            if not st.session_state.get('vlm_loaded', False):
                st.session_state.vlm_loading = True
            st.rerun()

        # --- Now create the text_area ---
        user_prompt = st.text_area(
            "Prompt for Vision Model",
            value=st.session_state.get("vision_prompt_input", DEFAULT_PROMPT),
            height=80,
            key="vision_prompt_input"
        )
        st.session_state["vision_prompt"] = user_prompt

        run_clicked = st.button(ACTION_BUTTON_NAME, use_container_width=True)
        if run_clicked:
            st.session_state["vision_prompt"] = user_prompt
            st.session_state.vision_result = None
            st.session_state.run_vision = True
            if not st.session_state.get('vlm_loaded', False):
                st.session_state.vlm_loading = True
            st.rerun()
    with col2:
        # Model setting logic (similar to app.py)
        # if 'vlm_loaded' not in st.session_state:
        #     st.session_state.vlm_loaded = False
        # if 'vlm_loading' not in st.session_state:
        #     st.session_state.vlm_loading = False

        # Model loading logic
        if st.session_state.get('vlm_loading', False) and not st.session_state.get('vlm_loaded', False):
            st.markdown(
                f'<div style="display:flex;align-items:center;">{ST_LOADING_HTML}<span style="font-size:1.1rem;"> Loading vision model {sthelpers.DEFAULT_VLM}...</span></div>',
                unsafe_allow_html=True
            )
            if not stub:
                success, stub, channel = sthelpers.aab_connect()
            try:
                print(model.set_model(stub, sthelpers.DEFAULT_MODEL_PATH, sthelpers.DEFAULT_VLM, sthelpers.DEFAULT_EMBEDDER, sthelpers.DEFAULT_RANKER))
            except Exception as e:
                st.error(f"Error loading model: {e}. Default model will be used.")
            st.session_state.vlm_loading = False
            st.session_state.vlm_loaded = True
            st.rerun()

        # Vision model inference logic and output
        text_placeholder = st.empty()
        if st.session_state.get('vlm_loaded', False) and not st.session_state.get('vlm_loading', False):
            if st.session_state.get('run_vision', False):
                if st.session_state.get('vision_result') is None:
                    prompt = st.session_state.get("vision_prompt", DEFAULT_PROMPT)
                    if not stub:
                        success, stub, channel = sthelpers.aab_connect()
                    try:
                        text_placeholder.markdown(
                            f'<div style="display:flex;align-items:center;">{ST_LOADING_HTML}<span style="font-size:1.1rem;"> Working... waiting for vision model response.</span></div>',
                            unsafe_allow_html=True
                        )  

                        image_prompt_option = chat.get_prompt_options({'name': 'QueryImagesPrompt'})
                        response_iter = chat.set_chat_request(stub, prompt=prompt, session_id=None, attachments=attachedFiles, prompt_options=image_prompt_option)
                        result = sthelpers.parse_streaming_response(chat.get_chat_response(response_iter, verbose=False))
                        st.session_state.vision_result = result
                        st.session_state.run_vision = False
                        text_placeholder.markdown(result or "*No response*", unsafe_allow_html=False)
                    except Exception as e:
                        st.session_state.run_vision = False
                        st.error(f"Vision model error: {e}")
                else:
                    text_placeholder.markdown(st.session_state.vision_result or "*No response*", unsafe_allow_html=False)
            else:
                text_placeholder.markdown(st.session_state.get('vision_result', ''), unsafe_allow_html=False)
        else:
            text_placeholder.markdown(st.session_state.get('vision_result', ''), unsafe_allow_html=False)
# Add a link back to the Translator page at the bottom (optional)
st.markdown('<a href="/app" target="_self">← Back to Translator</a>', unsafe_allow_html=True)