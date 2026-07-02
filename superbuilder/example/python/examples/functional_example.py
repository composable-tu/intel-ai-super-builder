import json
import grpc
import helpers.parameters as param
import helpers.config as config

def set_max_token_parameter(stub):
    try:
        # Get the default configuration
        default_config = config.get_config(stub)

        # Parse the 'parameters' field inside 'ActiveAssistant'
        default_config_parameters = json.loads(default_config["ActiveAssistant"]["parameters"])  # Parse the 'parameters' field as JSON

        # Extract and print the default max_token parameter value
        default_max_token = default_config_parameters["categories"][0]["fields"][0]
        print("\nDefault max_token:\n", default_max_token)

        # Decide which new max_token parameter value to use, to ensure it differs from the current value, allowing the user to easily verify the change
        if default_max_token["user_value"] == json.loads(param.init_default_params().parameters_json)["categories"][0]["fields"][0]["user_value"]:
            print("\nSetting max_token parameter value to 888...")
            new_parameters = param.set_max_token()
        else:
            print("\nSetting max_token parameter value to 500...")
            new_parameters = param.init_default_params()

        # Set max_token parameter using the stub
        param.set_parameters(stub, new_parameters)

        # Verify the max_token parameter in the database
        updated_config = config.get_config(stub)
        updated_config_parameters = json.loads(updated_config["ActiveAssistant"]["parameters"])
        updated_max_token = updated_config_parameters["categories"][0]["fields"][0]
        print("\nUpdated max_token:\n", updated_max_token)

        print("\nThe max_token value has been successfully updated from {} to {}.".format(
            default_max_token["user_value"], updated_max_token["user_value"]
        ))
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
    except Exception as e:
        print(f"Error: {e}")