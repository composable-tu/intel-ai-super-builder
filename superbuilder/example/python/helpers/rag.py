import grpc
import os
import json
from tqdm import tqdm
import superbuilder_service_pb2 as sb

def is_valid_file_path(file_path):
    """
    Check if the given file path is valid.
    
    Args:
        file_path (str): The file path to check.
    
    Returns:
        bool: True if the file path is valid, False otherwise.
    """
    return os.path.isfile(file_path)

def upload_file_to_knowledge_base(stub, file_paths):
    """
    Upload files to the knowledge base.
    
    Args:
        stub: The gRPC stub for making requests.
        file_paths (list): List of file paths to upload.
    """
    absolute_file_paths = []
    for file_path in file_paths:
        abs_path = os.path.abspath(file_path)
        if not is_valid_file_path(abs_path):
            print(f"Invalid file path: {abs_path}")
            continue
        absolute_file_paths.append(abs_path)
    
    if not absolute_file_paths:
        print("No valid file paths to upload.")
        return
    
    print("Files to Upload: ", absolute_file_paths)
    file_paths_str = json.dumps(absolute_file_paths)
    request = sb.AddFilesRequest(filesToUpload=file_paths_str)

    progress_bar = tqdm(desc="Uploading", unit="%")
    try:
        for response in stub.AddFiles(request):
            if "Error" in response.filesUploaded:
                raise Exception(f"File upload failed: {response.filesUploaded}")
            
            progress_bar.n = int(response.currentFileProgress)
            progress_bar.refresh()
    except grpc.RpcError as e:
        print(f"File upload failed: {e.details()}")
    finally:
        progress_bar.close()

def remove_uploaded_file(stub, file_paths):
    """
    Remove uploaded files from the knowledge base.
    
    Args:
        stub: The gRPC stub for making requests.
        file_paths (list): List of file paths to remove.
    """
    absolute_file_paths = []
    for file_path in file_paths:
        abs_path = os.path.abspath(file_path)
        if not is_valid_file_path(abs_path):
            print(f"Invalid file path: {abs_path}")
            continue
        absolute_file_paths.append(abs_path)
    
    if not absolute_file_paths:
        print("No valid file paths to upload.")
        return
    
    print("Files to Remove: ", absolute_file_paths)
    file_paths_str = json.dumps(absolute_file_paths)
    request = sb.RemoveFilesRequest(filesToRemove=file_paths_str)
    try:
        response = stub.RemoveFiles(request)
        if "Error" in response.filesRemoved:
            raise Exception(response.filesRemoved)
        print(f"File removed: {response.filesRemoved}")
    except grpc.RpcError as e:
        print(f"File removal failed: {e.details()}")

def list_uploaded_files(stub):
    """
    List all uploaded files in the knowledge base.
    
    Args:
        stub: The gRPC stub for making requests.

    Returns:
        list: A list of uploaded files if successful
    """
    request = sb.GetFileListRequest(fileType="")
    try:
        response = stub.GetFileList(request)
        uploaded_filepaths = []
        print("Uploaded Files:")
        for file in json.loads(response.fileList):
            uploaded_filepaths.append(file[0])
            print(file)
        return uploaded_filepaths
    except grpc.RpcError as e:
        print(f"Failed to list uploaded files: {e.details()}")