import superbuilder_service_pb2 as sb

def init_default_params():
    parametersReq = sb.SetParametersRequest(
        parameters_json="{\"categories\":[{\"name\":\"LLM\",\"description\":\"Modify chat model settings\",\"fields\":[{\"name\":\"max_token\",\"description\":\"Controls the LLM generation token limit. Higher value: Allows responses to be longer, but longer generation times. Lower value: Makes responses shorter, but quicker generation times.\",\"default_value\":1024,\"user_value\":500,\"min\":100,\"max\":1024}]}]}"
    )
    return parametersReq

def set_max_token():
    parametersReq = sb.SetParametersRequest(
        parameters_json="{\"categories\":[{\"name\":\"LLM\",\"description\":\"Modify chat model settings\",\"fields\":[{\"name\":\"max_token\",\"description\":\"Controls the LLM generation token limit. Higher value: Allows responses to be longer, but longer generation times. Lower value: Makes responses shorter, but quicker generation times.\",\"default_value\":1024,\"user_value\":888,\"min\":100,\"max\":1024}]}]}"
    )
    return parametersReq

def set_parameters(stub, params):
    reply = stub.SetParameters(params)
    return reply