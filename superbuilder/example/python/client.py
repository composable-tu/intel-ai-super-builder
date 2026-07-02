import os
import sys
import time
import signal
import grpc

import helpers.mw as mw
import helpers.chat as chat

from examples.chat_examples import (
    simple_chat,
    simple_chat_w_rag_specific_files,
    simple_chat_w_rag_all_files,
    simple_chat_w_image_query,
    workflow_summarize,
    workflow_query_tables,
    workflow_score_resumes,
    workflow_score_documents
)
from examples.functional_example import set_max_token_parameter
from examples.client_examples import switch_model

# Unset proxy environment variables
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

# Disable the proxy by setting the environment variable
os.environ["grpc.enable_http_proxy"] = "0"

stub = None
channel = None

def signal_handler(sig, frame):
    global stub
    print("Stopping execution.")
    if stub is not None:
        print("Disconnecting AAB")
        mw.disconnect(stub, channel)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def run_examples():
    complete = False

    print("\n========================================")
    actionInput = ("Select which example to run:\n"
                  "1. Execute simple chat\n"
                  "2. Execute simple chat with Knowledge Base (specific files)\n"
                  "3. Execute simple chat with Knowledge Base (all files)\n"
                  "4. Execute Image Query\n"
                  "5. Workflow: Summarize documents\n"
                  "6. Workflow: Query tables\n"
                  "7. Workflow: Score resumes\n"
                  "8. Workflow: Score documents\n"
                  "9. Set max_token parameter value\n\n"
                  "0. Exit\n\nEnter number: ")
    option = input(actionInput).strip().lower()
    if option == "0":
        print("Exiting...")
        complete = True
    elif option == "1":
        print("Executing simple chat example...")
        simple_chat(stub)
        complete = True
    elif option == "2":
        print("Executing simple chat with knowledge base (specific files) example...")
        simple_chat_w_rag_specific_files(stub)
        complete = True
    elif option == "3":
        print("Executing simple chat with knowledge base (all files) example...")
        simple_chat_w_rag_all_files(stub)
        complete = True
    elif option == "4":
        print("Executing image query example...")
        simple_chat_w_image_query(stub)
        complete = True
    elif option == "5":
        print("Executing workflow: summarize documents...")
        workflow_summarize(stub)
        complete = True
    elif option == "6":
        print("Executing workflow: query tables...")
        workflow_query_tables(stub)
        complete = True
    elif option == "7":
        print("Executing workflow: score resumes...")
        workflow_score_resumes(stub)
        complete = True
    elif option == "8":
        print("Executing workflow: score documents...")
        workflow_score_documents(stub)
        complete = True
    elif option == "9":
        print("Setting max_token parameter value...")
        set_max_token_parameter(stub)
        complete = True
    ## This option is not available as getting 'ERROR: Access to the path 'UDDC0C1.tmp' is denied.'
    # elif option == "4":
    #     print("Executing model switch example...")
    #     switch_model(stub)
    #     complete = True
    else:
        raise Exception('Invalid option. Exiting.')

    return complete, option

def main():
    # Connect to the AAB
    global successfulConnect, stub, channel
    grpc_address = 'localhost:5006'
    channel = grpc.insecure_channel(grpc_address)
    for attempt in range(5):
        successfulConnect, stub = mw.connect(channel)
        if successfulConnect:
            print("Connected successfully!")
            break
        else:
            print(f"Connection attempt {attempt + 1} failed. Retrying...\n")
            time.sleep(5)
    if successfulConnect:
        llm_ready = mw.check_pybackend(stub)
        if llm_ready:
            print("LLM backend is ready.")
            chat.warmup(stub)
            while True:
                try:
                    complete, example = run_examples()
                    if complete and example != "0":
                        print(f"\n\nExample {example} completed.")
                        continue
                    else:
                        mw.disconnect(stub, channel)
                        break
                except Exception as e:
                    print(f"Error: {e}")
                    mw.disconnect(stub, channel)
                    break
        else:
            print("LLM backend is not ready. Exiting.")
            mw.disconnect(stub, channel)
            exit()
    else:
        print("Connection failed. Exiting.")


if __name__ == '__main__':
    main()
        