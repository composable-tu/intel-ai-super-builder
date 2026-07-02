import json
import time
import unittest
import grpc
from unittest.mock import patch
import superbuilder_service_pb2_grpc as sb_grpc
from helpers.parameters import set_parameters, init_default_params, set_max_token
import helpers.config as config

class TestParametersHelpers(unittest.TestCase):

    def setUp(self):
        time.sleep(10)  # Allow time for the service to start
        # Connect to the actual service
        self.grpc_address = 'localhost:5006'
        self.channel = grpc.insecure_channel(self.grpc_address)
        self.stub = sb_grpc.SuperBuilderStub(self.channel)

    def tearDown(self):
        # Close the gRPC channel
        self.channel.close()

    @patch('helpers.parameters.sb.SetParametersRequest')
    def test_init_default_params(self, MockSetParametersRequest):
        params = init_default_params()
        MockSetParametersRequest.assert_called_once_with(
           parameters_json="{\"categories\":[{\"name\":\"LLM\",\"description\":\"Modify chat model settings\",\"fields\":[{\"name\":\"max_token\",\"description\":\"Controls the LLM generation token limit. Higher value: Allows responses to be longer, but longer generation times. Lower value: Makes responses shorter, but quicker generation times.\",\"default_value\":1024,\"user_value\":500,\"min\":100,\"max\":1024}]}]}"
        )
        self.assertEqual(params, MockSetParametersRequest(), "Test init_default_params failed")

    def test_set_parameters(self):
        try:
            # Get the default configuration
            default_config = config.get_config(self.stub)

            # Parse the 'parameters' field inside 'ActiveAssistant'
            default_config_parameters = json.loads(default_config["ActiveAssistant"]["parameters"])  # Parse the 'parameters' field as JSON

            # Extract and print the default max_token parameter value
            default_max_token = default_config_parameters["categories"][0]["fields"][0]
            print("\nDefault max_token:\n", default_max_token)

            # Decide which new max_token parameter value to use, to ensure it differs from the current value, allowing the user to easily verify the change
            if default_max_token["user_value"] == json.loads(init_default_params().parameters_json)["categories"][0]["fields"][0]["user_value"]:
                print("\nSetting max_token parameter value to 888...")
                new_parameters = set_max_token()
            else:
                print("\nSetting max_token parameter value to 500...")
                new_parameters = init_default_params()

            # Set max_token parameter using the stub
            set_parameters(self.stub, new_parameters)

            # Verify the max_token parameter in the database
            updated_config = config.get_config(self.stub)
            updated_config_parameters = json.loads(updated_config["ActiveAssistant"]["parameters"])
            updated_max_token = updated_config_parameters["categories"][0]["fields"][0]
            print("\nUpdated max_token:\n", updated_max_token)

            # Assert that the parameter value was updated correctly
            self.assertEqual(updated_max_token["user_value"], json.loads(new_parameters.parameters_json)["categories"][0]["fields"][0]["user_value"], "Parameter value was not updated correctly.")

            print("\nThe max_token value has been successfully updated from {} to {}.".format(
                default_max_token["user_value"], updated_max_token["user_value"]
            ))
        except grpc.RpcError as e:
            self.fail(f"gRPC error: {e.details()}")
        except Exception as e:
            self.fail(f"Error: {e}")

if __name__ == '__main__':
    unittest.main()