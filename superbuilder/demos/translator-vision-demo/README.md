# Vision & Translation demos on local AI PC with Intel AI Assistant Builder

This project is a collection of SuperBuilder Service API demos using Streamlit framework. It contains example using local LLM for vision and and translation tasks. 

It supports image upload, vision model inference (receipt scanning, image labeling), and text translation, all with a modern two-panel UI and loading feedback.

---

## Prerequisites

 - Intel AI Assistant Builder v1.2.1 or above
 - You have Qwen2.5-7B-Instruct-int4-ov and Phi-3.5-vision-instruct-int4-ov downloaded using AI Assistant Builder
---


## Features

- **Vision Model Demo**:  
  - Upload an image (receipt or general image)
  - Choose a quick action: "Scan Receipt" or "Label Image"
  - Edit the prompt or enter your own
  - Run vision model inference and view markdown-formatted results

- **Translation Demo**:  
  - (See `app.py`) Translate text using a language model backend

- **gRPC Backend**:  
  - Connects to AI Assistant Builder Service for model inference

- **User Experience**:  
  - Responsive two-panel layout
  - Loading GIF and clear status messages during model loading and inference
  - Markdown rendering for model replies

---


## Example: Direct AI Assistant Builder service API Calls

Below are code snippets from this demo, showing how to connect to the Builder backend, get configuration, set the model, and run a chat/translation.

```python
# Connect to the gRPC service
success, stub, channel = sthelpers.aab_connect()
if not success:
    print("Failed to connect to gRPC backend")
    # handle error or exit

# Get config from the backend
resp = config.get_config(stub)
print("Config:", resp)

# Set the model (example for LLM)
resp = model.set_model(stub, sthelpers.DEFAULT_MODEL_PATH, sthelpers.DEFAULT_LLM, sthelpers.DEFAULT_EMBEDDER, sthelpers.DEFAULT_RANKER)
print(resp)

# Run a chat (translation example)
prompt = f"Help me translate the following text into American English. Do not show thinking. </no_think>\n\n {batches[next_batch_idx]}"
response_iter = chat.set_chat_request(stub, prompt)

# Stream and parse the response (for translation)
translated = sthelpers.stream_and_parse_translation(
    chat.get_chat_response(response_iter, verbose=False),
    text_placeholder,
    translated_batches
)
```

- `sthelpers.aab_connect()` connects to the gRPC backend and returns the stub for API calls.
- `config.get_config(stub)` fetches the current backend configuration.
- `model.set_model(stub, sthelpers.DEFAULT_MODEL_PATH, sthelpers.DEFAULT_LLM, sthelpers.DEFAULT_EMBEDDER, sthelpers.DEFAULT_RANKER)` sets the active model.
- `chat.set_chat_request(stub, prompt)` sends a chat or translation request.
- `sthelpers.stream_and_parse_translation(...)` streams and displays the translation result.

You can find these usages in `app.py` and `sthelpers/stream_utils.py` in this demo.


```
sales-demo/
│
├── python-prototype/
│   ├── app.py                # Main translation demo app
│   ├── pages/
│   │   └── vision.py         # Vision model demo page
│   ├── sthelpers/
│   │   └── stream_utils.py   # Streamlit helper utilities
│   ├── loading_animation.gif # Loading spinner GIF
│   └── ...
│
└── example/
    └── python/
        └── helpers/
            ├── chat.py
            ├── config.py
            ├── model.py
            └── mw.py
```

---

## Setup

1. **Install dependencies**  
   (Recommended: use a virtual environment)
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit app**
   ```bash
   streamlit run python-prototype/app.py
   ```

3. **Access the Vision Demo**
   - In the Streamlit sidebar, select the "Vision Demo" page.

---

## Usage

- **Vision Demo**
  1. Upload a `.png`, `.jpg`, or `.jpeg` image.
  2. Use "Scan Receipt" or "Label Image" for quick prompts, or enter your own prompt.
  3. Click "Run Analysis" to send the request to the vision model.
  4. View the markdown-formatted output in the right panel.

- **Translation Demo**
  - Enter text and select translation options in the main app page.

---

## Customization

- **Prompts**:  
  Edit `DEFAULT_RECEIPT_SCAN_PROMPT`, `DEFAULT_IMG_LABEL_PROMPT`, or `DEFAULT_PROMPT` in `vision.py` to change default behaviors.

- **Loading GIF**:  
  Replace `loading_animation.gif` in `python-prototype/` with your own spinner if desired.

- **gRPC Backend**:  
  Update connection details in `sthelpers/stream_utils.py` as needed.

---

## Troubleshooting

- **Helpers Import Error**:  
  Ensure your `PYTHONPATH` or `sys.path` includes `example/python` so `helpers` modules can be imported.

- **Loading GIF Not Showing**:  
  The app uses an absolute path to `loading_animation.gif`. Make sure the file exists at `python-prototype/loading_animation.gif`.

---

## License

MIT License (or your preferred license)

---

## Credits

- Built with [Intel AI Assistant Builder](#),  [Streamlit](https://streamlit.io/)

---

*For questions or contributions, please open an issue or pull request!*