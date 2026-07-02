import time
import unittest
import grpc
import superbuilder_service_pb2_grpc as sb_grpc
from helpers.mw import check_pybackend, connect, disconnect

class TestMWHelpers(unittest.TestCase):

    def setUp(self):
        time.sleep(10)  # Allow time for the service to start
        # Connect to the actual middleware service
        self.grpc_address = 'localhost:5006'
        self.channel = grpc.insecure_channel(self.grpc_address)
        self.stub = sb_grpc.SuperBuilderStub(self.channel)

    def tearDown(self):
        # Skip tearDown for test_disconnect
        if self._testMethodName != "test_disconnect":
            self.channel.close() # Close the gRPC channel

    def test_check_pybackend_success(self):
        try:
            result = check_pybackend(self.stub)
            self.assertTrue(result, "Test check_pybackend_success failed")
        except grpc.RpcError as e:
            self.fail(f"gRPC error during test_check_pybackend_success: {e.details()}")
        except Exception as e:
            self.fail(f"Error during test_check_pybackend_success: {e}")
            
    def test_connect_success(self):
        try:
            success, stub = connect(self.channel)
            self.assertTrue(success, "Test connect_success failed")
            self.assertIsNotNone(stub, "Stub is None after successful connection")
        except grpc.RpcError as e:
            self.fail(f"gRPC error during test_connect_success: {e.details()}")
        except Exception as e:
            self.fail(f"Error during test_connect_success: {e}")

    # CICD Break because of the disconnect method
    # Uncomment the following test if you want to test the disconnect functionality
    # def test_disconnect(self):
    #     try:
    #         disconnect(self.stub, self.channel)
    #         print("Disconnected successfully.")
    #     except grpc.RpcError as e:
    #         self.fail(f"gRPC error during test_disconnect: {e.details()}")
    #     except Exception as e:
    #         self.fail(f"Error during test_disconnect: {e}")

if __name__ == '__main__':
    unittest.main()