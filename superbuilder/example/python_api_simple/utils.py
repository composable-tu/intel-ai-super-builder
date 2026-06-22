import sys
import os
from typing import Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'example', 'python')))
import json
import grpc
import time
from tqdm import tqdm

import superbuilder_service_pb2 as sb
import superbuilder_service_pb2_grpc as sbg

GRPC_ADDRESS = 'localhost:5006'

DEFAULT_MODEL_PATH = "C:\\ProgramData\\IntelAIA\\local_models"
DEFAULT_VLM = "Phi-3.5-vision-instruct-int4-ov"
DEFAULT_LLM = 'Qwen3-8B-int4-ov'
DEFAULT_EMBEDDER = 'bge-base-en-v1.5-int8-ov'
DEFAULT_RANKER = 'bge-reranker-base-int8-ov'


def check_middleware(stub):
    try:
        print("Calling superbuilder service APIs: SayHello()")
        response = stub.SayHello(sb.SayHelloRequest(
            name='API'))
        if not response.message:
            return False
        return response.message
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
        return False


def check_pybackend(stub):
    try:
        print("Calling superbuilder service APIs: SayHelloPyllm()")
        helloPyllmResponse = stub.SayHelloPyllm(sb.SayHelloRequest(
            name='SuperBuilder Python Clients!'))
        if not helloPyllmResponse:
            return False
        return helloPyllmResponse.message=="ready"
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
        return False

def load_models(stub):
    try:
        print("Calling APIs: LoadModels()")
        response = stub.LoadModels(sb.LoadModelsRequest())
        if not response:
            return False
        return response.status
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
        return False

def aab_connect():

    success = False
    stub = None
    channel = grpc.insecure_channel(GRPC_ADDRESS)
    try:
        grpc.channel_ready_future(channel).result(timeout=15)  # Wait until the channel is ready
        stub = sbg.SuperBuilderStub(channel)
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
    except grpc.FutureTimeoutError:
        print("gRPC channel connection busy or missing")
    else:
        success = True
    
    return success, stub, channel


def disconnect(stub, channel):
    if stub is not None:
        stub.DisconnectClient(sb.DisconnectClientRequest())
    if channel is not None:
        channel.close()


def parse_streaming_response(response_iter):
    reply = ""
    for resp in response_iter:
        if not resp:
            continue

        reply += resp  # Append streamed text
        time.sleep(0.01)  # for smooth streaming effect

    return reply



def get_config(stub):
    response = stub.GetClientConfig(sb.GetClientConfigRequest())
    return json.loads(response.data)

def set_config(stub, assistant, config_data):
    response = stub.SetActiveAssistant(sb.SetActiveAssistantRequest(assistant=assistant, models_json=config_data))
    return response.message

def download(stub, url, local_path, token_id: Optional[str] = None):
    """    
    Downloads a file from the specified URL to the local path using SuperBuilder's gRPC service.
    """
    progress_bar = tqdm(desc="Downloading", unit="%")
    try:
        for response in stub.DownloadFiles(sb.DownloadFilesRequest(FileUrl=url, localPath=local_path, tokenId=token_id)):
            print(response.FileDownloaded)
            if int(response.progress) < 0:
                continue
            if "ERROR" in response.FileDownloaded:
                raise Exception(response.FileDownloaded)
            
            progress_bar.n = int(response.progress)
            progress_bar.refresh()
            if int(response.progress) == 100:
                break
    except grpc.RpcError as e:
        print(f"download failed: {e.details()}")

def set_model(stub, local_model_path, llm, embedder, ranker):
    llm = os.path.join(local_model_path, llm)
    embedder = os.path.join(local_model_path, embedder)
    ranker = os.path.join(local_model_path, ranker)

    try:
        print("Loading Models...")
        return stub.SetModels(sb.SetModelsRequest(llm=llm, embedder=embedder, ranker=ranker))
    except Exception as e:
        return e
