import time
import chat
import utils
import json
from pprint import pprint





def silent_install():
    pass


def silent_uninstall():
    pass


def silent_update():
    pass


is_model_ready = False
is_chat_ready = False
is_rag_ready = False

def superbuilder_status(stub):
    """
    Check the status of the SuperBuilder middleware service.
    """
    return utils.check_middleware(stub)

def llm_status(stub):
    """
    Check the status of the LLM (Language Model) backend service.
    SuperBuilder models, including RAG ones are ready
    when pybackend call returns ready.
    """
    is_chat_ready = utils.check_pybackend(stub)
    is_model_ready = utils.load_models(stub)
    is_rag_ready = is_model_ready
    return {"chat_ready": is_chat_ready, "model_ready": is_model_ready, "rag_ready": is_rag_ready}

def get_software_update():
    """
     Check for software updates from the SuperBuilder service.
     This pulls the latest software update manifest xml form SuperBuilder web portal
     
     """
    response = stub.GetSoftwareUpdate(utils.sb.SayHelloRequest(name='update'))
    if not response.message:
        return False
    print("Software Update returned: " + response.message)


def download_installer(stub):
    url = "https://aibuilder.intel.com/installers/Intel(R)%20AI%20Assistant%20Builder_Installer_SA_2.1.0.925.exe"
    local_path = "C:\\temp\\Intel_AI_Assistant_Builder_Installer.exe"
    return utils.download(stub, url, local_path)


def download_model(stub):
    url = "https://huggingface.co/OpenVINO/Qwen2.5-7B-Instruct-int4-ov"
    local_path = "C:\\temp\\models\\Qwen2.5-7B-Instruct-int4-ov" 
    
    return utils.download(stub, url, local_path)

def set_models(stub, model_path):    
    import os

    llm_path = os.path.join(model_path, utils.DEFAULT_LLM)
    embedder_path = os.path.join(model_path, utils.DEFAULT_EMBEDDER)
    ranker_path = os.path.join(model_path, utils.DEFAULT_RANKER)
    if os.path.exists(llm_path) and os.path.exists(embedder_path) and os.path.exists(ranker_path):
        response = utils.set_model(stub, utils.DEFAULT_MODEL_PATH, utils.DEFAULT_LLM, utils.DEFAULT_EMBEDDER, utils.DEFAULT_RANKER)
    else:
        print("Models not found")
    return response

def assistant_status(stub):
    config = utils.get_config(stub)

    return config.get('ActiveAssistant', {}) if config else {}


success = False
stub = None
channel = None

def aab_init():
    global success, stub, channel
    success, stub, channel = utils.aab_connect()    
    if not success:
        print("Failed to connect to SuperBuilder")
        return
    return success, stub, channel 

SHOW_ASSISTANT_STATUS = False
SHOW_MODEL_DOWNLOAD = False

def main():
    success, stub, channel = aab_init()
    
    if not success:
        print("Failed to connect to SuperBuilder")
        return

    try:
        print("\n=== App Starts ===", )
        print("Current  Time / 当前时间", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) 

        print("\n=== SuperBuilderStatus / 当前的SuperBuilder状态 ===")
        status = superbuilder_status(stub)
        if isinstance(status, str) and status:
            try:
                status = json.loads(status)
            except json.JSONDecodeError:
                print(f"Raw response: {status}")
                status = {"error": "Invalid JSON response"}
        pprint(status, width=120, sort_dicts=False)
        
        print("\n=== LLM Status ===")        
        llm = llm_status(stub)
        if isinstance(llm, str) and llm:
            try:
                llm = json.loads(llm)
            except json.JSONDecodeError:
                print(f"Raw response: {llm}")
                llm = {"error": "Invalid JSON response"}
        pprint(llm, width=120, sort_dicts=False)
        
        print("\n=== ChatEnable / 开启协议 ===")
        print(f"Chat Ready: {llm['chat_ready']}")
        
        print("\n=== ModelStatus ===")
        print(f"Model Ready: {llm['model_ready']}")

        print("\n=== RagEnable / 开启RAG功能 ===")
        print(f"RAG Ready: {llm['rag_ready']}")

        if SHOW_ASSISTANT_STATUS:
            print("\n=== Assistant Status ===")
            res = assistant_status(stub)
            assistant_name = res.get('full_name', {})
            assistant_models = res.get('models', {})
            print(f"Assistant Name: {assistant_name}")
            pprint(assistant_models, width=120, sort_dicts=False)

        if SHOW_MODEL_DOWNLOAD:
            print("\n=== Download / 下载SuperBuilder ===")
            print("Downloading latest installer from Intel web portal...")
            print("Skipping the actual download in this demo")
            # download_installer(stub)

            print("\n=== Download / 下载 Model ===")
            print("Downloading latest installer from Intel web portal...")
            print("Skipping the actual download in this demo")
            # download_model(stub)

            print("\n=== Load Model ===")
            model_path = utils.DEFAULT_MODEL_PATH        
            print(f"set models from: {model_path}")        
            # print("(Skipping actual model loading)")
            # set_models(stub, model_path)

        print("Current  Time / 当前时间", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) 

        if llm["chat_ready"]:
            try:
                prompt = "Hello, who are you?"
                print("Simple chat: ", prompt)
                session_id = chat.init_chat_session(stub)
                response_iterator = chat.set_chat_request(stub, prompt, session_id)
                chat.get_chat_response(response_iterator, verbose=True)
                chat.remove_session(stub, session_id)
            except Exception as e:
                print(f"Error: {e}")

        print("Current  Time / 当前时间", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) 
        print("\n=== App Ends ===", )

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("\n=== Disconnect ===")
        print("Disconnecting from SuperBuilder...")
        utils.disconnect(stub, channel)


if __name__ == "__main__":
    main()