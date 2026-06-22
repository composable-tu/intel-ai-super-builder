import time
import unittest
import grpc
import superbuilder_service_pb2_grpc as sb_grpc
from helpers.config import get_config, set_config

class TestConfigHelpers(unittest.TestCase):

    def setUp(self):
        time.sleep(10)  # Allow time for the service to start
        # Connect to the actual service
        self.grpc_address = 'localhost:5006'
        self.channel = grpc.insecure_channel(self.grpc_address)
        self.stub = sb_grpc.SuperBuilderStub(self.channel)

    def tearDown(self):
        # Close the gRPC channel
        self.channel.close()

    def test_get_config(self):
        try:
            # Call the actual middleware API to get the configuration
            result = get_config(self.stub)

            # Validate the result
            self.assertIsInstance(result, dict, "Config is not a dictionary")
            self.assertIn("ActiveAssistant", result, "ActiveAssistant key missing in config")
        except grpc.RpcError as e:
            self.fail(f"gRPC error during test_get_config: {e.details()}")
        except Exception as e:
            self.fail(f"Error during test_get_config: {e}")

    def test_set_config(self):
        try:
            # Prepare test data
            assistant = "HR"
            config_data = "[]"

            # Call the actual middleware API to set the configuration
            response_message = set_config(self.stub, assistant, config_data)

            # Validate the response
            self.assertEqual(response_message, "Assistant set successfully", "Failed to set config")

            # Call get_config to verify the short_name
            result = get_config(self.stub)

            # Validate the short_name in the configuration
            self.assertIn("ActiveAssistant", result, "ActiveAssistant key missing in config")
            self.assertEqual(result["ActiveAssistant"]["short_name"], assistant, f"short_name is not set to {assistant}")
        except grpc.RpcError as e:
            self.fail(f"gRPC error during test_set_config: {e.details()}")
        except Exception as e:
            self.fail(f"Error during test_set_config: {e}")

if __name__ == '__main__':
    unittest.main()