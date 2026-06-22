import time
import unittest
import os
import grpc
import superbuilder_service_pb2_grpc as sb_grpc
from helpers.rag import is_valid_file_path, upload_file_to_knowledge_base, remove_uploaded_file, list_uploaded_files

class TestRagHelpers(unittest.TestCase):

    def setUp(self):
        time.sleep(10)  # Allow time for the service to start
        # Connect to the actual service
        self.grpc_address = 'localhost:5006'
        self.channel = grpc.insecure_channel(self.grpc_address)
        self.stub = sb_grpc.SuperBuilderStub(self.channel)

    def tearDown(self):
        # Close the gRPC channel
        self.channel.close()

    def test_1_upload_file_to_knowledge_base(self):
        try:
            # Prepare test data
            file_path = ["examples/resources/Minimum Wages Order 2022.pdf"]
            absolute_file_path = [os.path.abspath(file_path[0])]  # Convert to absolute path

            # Call the actual middleware API to upload files
            upload_file_to_knowledge_base(self.stub, file_path)

            # Assert that the file appears in the list of uploaded files
            uploaded_files = list_uploaded_files(self.stub)
            self.assertIn(absolute_file_path[0], uploaded_files, f"File {absolute_file_path[0]} not found in uploaded files")
        except grpc.RpcError as e:
            self.fail(f"gRPC error during test_upload_file_to_knowledge_base: {e.details()}")
        except Exception as e:
            self.fail(f"Error during test_upload_file_to_knowledge_base: {e}")

    def test_2_remove_uploaded_file(self):
        try:
            # Prepare test data
            file_path = ["examples/resources/Minimum Wages Order 2022.pdf"]
            absolute_file_path = [os.path.abspath(file_path[0])]  # Convert to absolute path

            # Call the actual middleware API to remove files
            remove_uploaded_file(self.stub, file_path)
            
            # Assert that the file is removed from the list of uploaded files
            uploaded_files = list_uploaded_files(self.stub)
            self.assertNotIn(absolute_file_path[0], uploaded_files, f"File {absolute_file_path[0]} still found in uploaded files after removal")
        except grpc.RpcError as e:
            self.fail(f"gRPC error during test_remove_uploaded_file: {e.details()}")
        except Exception as e:
            self.fail(f"Error during test_remove_uploaded_file: {e}")

    def test_3_list_uploaded_files(self):
        try:
            # Call the actual middleware API to list uploaded files
            uploaded_files = list_uploaded_files(self.stub)

            # Assert that the response is a list
            self.assertIsInstance(uploaded_files, list, "Uploaded files response is not a list")
        except grpc.RpcError as e:
            self.fail(f"gRPC error during test_list_uploaded_files: {e.details()}")
        except Exception as e:
            self.fail(f"Error during test_list_uploaded_files: {e}")

if __name__ == '__main__':
    unittest.main()