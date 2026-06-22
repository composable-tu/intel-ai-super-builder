import os
import grpc
from tqdm import tqdm
import superbuilder_service_pb2 as sb
import helpers.config as config

def download(stub, url, local_path):
    progress_bar = tqdm(desc="Downloading", unit="%")
    try:
        for response in stub.DownloadFiles(sb.DownloadFilesRequest(FileUrl=url, localPath=local_path)):
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
        print(f"Model download failed: {e.details()}")

def set_model(stub, local_model_path, llm, embedder, ranker):
    llm = os.path.join(local_model_path, llm)
    embedder = os.path.join(local_model_path, embedder)
    ranker = os.path.join(local_model_path, ranker)

    try:
        print("Loading Models...")
        return stub.SetModels(sb.SetModelsRequest(llm=llm, embedder=embedder, ranker=ranker))
    except Exception as e:
        return e