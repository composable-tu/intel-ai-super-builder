import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'example', 'python')))
import json
import grpc

import helpers.mw as mw

# Constants

GRPC_ADDRESS = 'localhost:5006'

DEFAULT_MODEL_PATH = "C:\\ProgramData\\IntelAIA\\local_models"
DEFAULT_VLM = "Phi-3.5-vision-instruct-int4-ov"
DEFAULT_LLM = 'Qwen3-8B-int4-ov'
DEFAULT_EMBEDDER = 'bge-base-en-v1.5-int8-ov'
DEFAULT_RANKER = 'bge-reranker-base-int8-ov'

LOADING_GIF=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'loading_animation.gif'))


def get_loading_gif():
    import base64
    with open(LOADING_GIF, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    gif_html = f'<img src="data:image/gif;base64,{b64}" width="64" style="margin-right:10px;">'
    return gif_html

def aab_connect():
    global success, stub, channel
    channel = grpc.insecure_channel(GRPC_ADDRESS)
    success, stub = mw.connect(channel)
    return success, stub, channel

def parse_streaming_response(response_iter):
    reply = ""
    for resp in response_iter:
        if not resp:
            continue

        reply += resp  # Append streamed text
        time.sleep(0.01)  # for smooth streaming effect

    return reply

import time

def stream_and_parse_translation(response_iter, text_placeholder, translated_batches):
    """
    Streams and parses plain string responses,
    updating the Streamlit text area in real time.
    """
    reply = ""
    for resp in response_iter:
        if not resp:
            continue

        reply += resp  # Append streamed text

        # Update placeholder instead of creating new text_area each time
        text_placeholder.text_area(
            "Translated Content",
            '\n'.join([t for t in translated_batches if t] + [reply]),
            height=450
        )
        time.sleep(0.01)  # for smooth streaming effect

    return reply

