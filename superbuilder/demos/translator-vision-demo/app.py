import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..', 'example', 'python')))

import sthelpers.stream_utils as sthelpers

import streamlit as st
import grpc
import time

# Add example/python to sys.path for imports
import helpers.chat as chat
import helpers.config as config
import helpers.model as model
import superbuilder_service_pb2 as sb
import superbuilder_service_pb2_grpc as sbg
import json



def split_text_batches(text, batch_size=200):
    '''
    Helper to split text into batches of ~200 chars, only at newlines
    '''
    lines = text.splitlines(keepends=True)
    batches = []
    current = ''
    for line in lines:
        if len(current) + len(line) > batch_size and current:
            batches.append(current)
            current = ''
        current += line
    if current:
        batches.append(current)
    return batches

success = False
stub = None
channel = None
active_model = None

MAX_CONTENT_LENGTH = 5000
BATCH_SIZE = 200
ST_LOADING_HTML = sthelpers.get_loading_gif()

def main():
    global success, stub, channel, active_model
    st.set_page_config(layout="wide", page_title="Intel(R) AI Assistant Builder APIs", page_icon="🔤")
    st.markdown("""
        <style>
        .block-container {
            # padding-top: 12rem !important;
        }
        .dual-title {
            # margin-top: 2rem;
            # margin-bottom: 20px !important;
            font-size: 2.2rem;
            color: #222;
            font-weight: 700;
        }
        .dual-title span {
            font-size: 1.1rem;
            font-weight: 400;
            color: #444;
        }
        # Custom CSS for fixed-width dual panel, matching panel heights, and always-visible scrollbars
        .dual-panel-container {
            max-width: 1440px;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            flex-direction: row;
            gap: 24px;
            align-items: flex-start;
        }
        .dual-panel {
            flex: 1 1 0;
            min-width: 0;
            max-width: 100%;
            height: 500px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        /* Always show persistent vertical scrollbar for all Streamlit textareas */
        textarea[aria-label="File Content"],
        textarea[aria-label="Translated Content"] {
            overflow-y: scroll !important;
            overflow-x: hidden !important;
            min-height: 100px;
            scrollbar-gutter: stable both-edges;
            /* For Firefox */
            scrollbar-width: thin;
            scrollbar-color: #bbb #f0f0f0;
        }
        /* For Webkit browsers (Chrome, Edge, Safari) */
        textarea[aria-label="File Content"]::-webkit-scrollbar,
        textarea[aria-label="Translated Content"]::-webkit-scrollbar {
            width: 10px;
            background: #f0f0f0;
        }
        textarea[aria-label="File Content"]::-webkit-scrollbar-thumb,
        textarea[aria-label="Translated Content"]::-webkit-scrollbar-thumb {
            background: #bbb;
            border-radius: 6px;
        }                
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 class='dual-title'>Check AI Assistant Builder Service <span>(gRPC LLM)</span></h3>", unsafe_allow_html=True)

    # --- New Row: Ping SuperBuilder Service ---
    ping_col1, ping_col2 = st.columns([1, 3])
    with ping_col1:
        ping_clicked = st.button("Ping Local LLM Service", key="ping_superbuilder")

    if ping_clicked:
        try:
            success, stub, channel = sthelpers.aab_connect()
            if not success:
                st.session_state["ping_result"] = json.dumps({"error": "Failed to connect to gRPC backend"}, ensure_ascii=False, indent=2)
                st.stop()
            else:
                st.session_state["ping_result"] = "SuperBuilder service connected"    

            resp = config.get_config(stub)
            # Convert protobuf message to dict, then to pretty JSON
            pretty_json = json.dumps(resp, ensure_ascii=False, indent=2)
            st.session_state["ping_result"] = pretty_json
        except Exception as e:
            st.session_state["ping_result"] = json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)
        
    with ping_col2:
        ping_result = st.session_state.get("ping_result", "")

        # if ping_result:
        # Add this CSS once at the top of your app
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

        # Then use st.code as normal
        st.code(ping_result, language="json", height=300)
               

    ### Example - Translator
    st.markdown("<h3 class='dual-title'>Translator <span>(gRPC LLM)</span></h3>", unsafe_allow_html=True)

    # Controls row: file uploader and warning
    TEST_STRING = """注意：1、该方法在执行时，需要指定转换的日期时间；如果不指定，表示将自动对当前日期时间转换；2、该方法在执行时，需要一个特定的格式时间。格式字符如表所示。"""
    file_content = TEST_STRING
    warning = ''
    uploaded_file = st.file_uploader("Select a text file to translate", type=["txt"])
    if uploaded_file:
        file_content = uploaded_file.read().decode('utf-8')
        if len(file_content) > MAX_CONTENT_LENGTH:
            file_content = file_content[:MAX_CONTENT_LENGTH]
            warning = f"⚠️ File truncated to {MAX_CONTENT_LENGTH} characters."
    if warning:
        st.warning(warning)


    session_state = st.session_state

    if 'model_loaded' not in session_state:
        session_state.model_loaded = False
    if 'model_loading' not in session_state:
        session_state.model_loading = False

    # Ensure session state attributes are initialized
    if 'translated_batches' not in session_state:
        session_state.translated_batches = []
    if 'batches' not in session_state:
        session_state.batches = []

    col1, col2 = st.columns([1, 1])

    with col1:
        # If no file is uploaded, use the test string as the value
        left_value = file_content if uploaded_file else TEST_STRING
        st.text_area("File Content", left_value, height=450, key="left_text")
        translate_clicked = st.button("Translate to English", use_container_width=True)

        if translate_clicked:
            input_text = file_content if uploaded_file else TEST_STRING
            if not input_text.strip():
                st.warning("No input text to translate.")
            else:

                # If model is not loaded, trigger model loading
                if not session_state.model_loaded:
                    session_state.model_loading = True
                    session_state.pending_translation = {"input_text": input_text}
                    st.rerun()
                else:
                    # Prepare batches for translation
                    batches = split_text_batches(input_text, BATCH_SIZE)
                    session_state.batches = batches
                    session_state.translated_batches = [None] * len(batches)
                    session_state.streaming_text = ''
                    session_state.translating = True
                    session_state.translation_step_done = False
                    st.rerun()                
                # Prepare batches for translation
                batches = split_text_batches(input_text, BATCH_SIZE)
                session_state.batches = batches
                session_state.translated_batches = [None] * len(batches)
                session_state.streaming_text = ''
                session_state.translating = True
                session_state.translation_step_done = False
                st.rerun()

    import random, string
    # translating = None
    spinner_html = None
    # next_batch_idx = None

    with col2:

        # Model loading logic
        if session_state.get('model_loading', False):
            right_panel_container = st.container()
            spinner_html = (
                '<div style="background-color:#e6f0fa;padding:12px 16px;border-radius:6px;margin-bottom:8px;display:flex;align-items:center;">'
                f'{ST_LOADING_HTML}'
                f'<span style="font-size:1.05rem;color:#2563eb;vertical-align:middle;">Setting model {sthelpers.DEFAULT_LLM}... Please wait.</span>'
                '</div>'
            )
            right_panel_container.markdown(spinner_html, unsafe_allow_html=True)
            # Actually load the model
            if not stub:
                success, stub, channel = sthelpers.aab_connect()

            try:
                print(model.set_model(stub, sthelpers.DEFAULT_MODEL_PATH, sthelpers.DEFAULT_LLM, sthelpers.DEFAULT_EMBEDDER, sthelpers.DEFAULT_RANKER))
            except Exception as e:
                st.error(f"Error loading model: {e}. Default model will be used.")

            session_state.model_loading = False
            session_state.model_loaded = True
            # If translation was pending, start it now
            pending = session_state.pop("pending_translation", None)
            if pending:
                batches = split_text_batches(pending["input_text"], BATCH_SIZE)
                session_state.batches = batches
                session_state.translated_batches = [None] * len(batches)
                session_state.streaming_text = ''
                session_state.translating = True
                session_state.translation_step_done = False
                st.rerun()
            else:
                st.rerun()
            st.stop()

         # Always define translating before use
        translating = session_state.get('translating', False)
        batches = session_state.batches if translating else []
        translated_batches = session_state.translated_batches if translating else []
        next_batch_idx = None

        # Always show the right panel, even if no translation yet
        right_panel_container = st.container()
        # Default: show empty or previous translation
        translated_text = ''
        if uploaded_file and session_state.translated_batches:
            translated_text = '\n'.join([t for t in session_state.translated_batches if t])
        # Show the text area by default, and keep a reference to update its content
        text_placeholder = right_panel_container.empty()

        # Determine spinner state
        spinner_html = ""
        if session_state.get('model_loading', False):
            spinner_html = (
                '<div style="background-color:#e6f0fa;padding:12px 16px;border-radius:6px;margin-bottom:8px;display:flex;align-items:center;">'
                f'{ST_LOADING_HTML}'
                '<span style="font-size:1.05rem;color:#2563eb;vertical-align:middle;">Loading model... Please wait.</span>'
                '</div>'
            )
        elif translating and next_batch_idx is not None and not session_state.get('translation_step_done', False):
            # Only show spinner if translating and translation_step_done is False (about to do translation)
            spinner_html = (
                '<div style="background-color:#e6f0fa;padding:12px 16px;border-radius:6px;margin-bottom:8px;display:flex;align-items:center;">'
                f'{ST_LOADING_HTML}'
                '<span style="font-size:1.05rem;color:#2563eb;vertical-align:middle;">Translating... Please wait.</span>'
                '</div>'
            )            
        if spinner_html:
            right_panel_container.markdown(spinner_html, unsafe_allow_html=True)

        # --- RIGHT PANEL TRANSLATION STREAMING LOGIC ---

        # Always show the right panel's text area and spinner if needed
        right_panel_text = session_state.get('streaming_text', '')
        text_placeholder.text_area("Translated Content", right_panel_text, height=450, key="right_text_stream")

        # Streaming logic: if translating, do one step per rerun
        translating = session_state.get('translating', False)
        batches = session_state.batches if translating else None
        translated_batches = session_state.translated_batches if translating else None
        next_batch_idx = None
        if translating:
            for i, t in enumerate(translated_batches):
                if t is None:
                    next_batch_idx = i
                    break

        if translating and next_batch_idx is not None:
            # Show spinner
            spinner_html = (
                '<div style="background-color:#e6f0fa;padding:12px 16px;border-radius:6px;margin-bottom:8px;display:flex;align-items:center;">'
                '<img src="https://icons8.com/preloaders/preloaders/1495/Spinner-3.gif" width="24" style="vertical-align:middle;margin-right:10px;">'
                '<span style="font-size:1.05rem;color:#2563eb;vertical-align:middle;">Translating... Please wait.</span>'
                '</div>'
            )
            right_panel_container.markdown(spinner_html, unsafe_allow_html=True)
            scroll_right_panel_textarea()

            # Step 1: If translation_step_done is False, set it True and rerun (to show spinner)
            if not session_state.get('translation_step_done', False):
                session_state.translation_step_done = True
                st.rerun()
            # Step 2: If translation_step_done is True, do the translation step
            else:
                if not stub:
                    success, stub, channel = sthelpers.aab_connect()

                # --- Perform translation step ---
                prompt = f"Help me translate the following text into American English. Do not show thinking. </no_think>\n\n {batches[next_batch_idx]}"
                response_iter = chat.set_chat_request(stub, prompt)
                
                translated = sthelpers.stream_and_parse_translation(
                    chat.get_chat_response(response_iter, verbose=False),
                    text_placeholder,
                    session_state.translated_batches
                )
                channel.close()
                session_state.translated_batches[next_batch_idx] = translated
                session_state.streaming_text = '\n'.join([t for t in session_state.translated_batches if t])
                session_state.translation_step_done = False  # Reset for next batch
                st.rerun()
        elif translating:
            # All batches done
            session_state.translating = False
            session_state.translation_step_done = False
            session_state.streaming_text = '\n'.join([t for t in session_state.translated_batches if t])



# Reusable function to inject JS for auto-scrolling the right panel textarea
def scroll_right_panel_textarea():
    st.markdown("""
    <script>
    function scrollToBottom() {
      var right = document.querySelector('textarea[aria-label="Translated Content"]#sync-right-panel');
      if (right) {
        right.scrollTop = right.scrollHeight;
      }
      // Optionally scroll left to bottom as well
      // var left = document.querySelector('textarea[aria-label="File Content"]#sync-left-panel');
      // if (left) left.scrollTop = left.scrollHeight;
      assignSyncIdsAndListeners();
    }
    scrollToBottom();
    setTimeout(scrollToBottom, 30);
    setTimeout(scrollToBottom, 100);
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()