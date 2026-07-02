import grpc
import os
import sys
SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(SCRIPT_DIR,'..')))

import helpers.chat as chat
import helpers.rag as rag

def simple_chat(stub):
    try:
        prompt = "Who are you"

        session_id = chat.init_chat_session(stub)

        response_iterator = chat.set_chat_request(stub, prompt, session_id)
        response = chat.get_chat_response(response_iterator)
        chat.remove_session(stub, session_id)
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
    except Exception as e:
        print(f"Error: {e}")

def simple_chat_w_rag_specific_files(stub):
    try:
        file_paths = ["examples/resources/Minimum Wages Order 2022.pdf", "examples/resources/Mercy Baker - Resume.pdf"]
        specific_file_paths = ["examples/resources/Minimum Wages Order 2022.pdf"]
        prompt = "What is the minimum wages order for 2022 in Malaysia?"

        # Upload files to the knowledge base
        rag.upload_file_to_knowledge_base(stub, file_paths)
        rag.list_uploaded_files(stub)
        session_id = chat.init_chat_session(stub)

        # query only specific files in knowledge base
        response_iterator = chat.set_chat_request(stub, prompt, session_id, attachments=specific_file_paths)
        response = chat.get_chat_response(response_iterator)

        rag.remove_uploaded_file(stub, file_paths)
        chat.remove_session(stub, session_id)
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
    except Exception as e:
        print(f"Error: {e}")

def simple_chat_w_rag_all_files(stub):
    try:
        file_paths = ["examples/resources/Minimum Wages Order 2022.pdf", "examples/resources/Mercy Baker - Resume.pdf"]
        prompt1 = "What is the minimum wages order for 2022 in Malaysia?"
        prompt2 = "Where did Mercy Baker study?"

        # Upload the files to the knowledge base
        rag.upload_file_to_knowledge_base(stub, file_paths)
        rag.list_uploaded_files(stub)
        session_id = chat.init_chat_session(stub)

        # query all files in knowledge base
        response_iterator = chat.set_chat_request(stub, prompt1, session_id, attachments=None)
        response = chat.get_chat_response(response_iterator)

        # query all files in knowledge base
        response_iterator = chat.set_chat_request(stub, prompt2, session_id, attachments=None)
        response = chat.get_chat_response(response_iterator)

        rag.remove_uploaded_file(stub, file_paths)
        chat.remove_session(stub, session_id)
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
    except Exception as e:
        print(f"Error: {e}")

def simple_chat_w_image_query(stub):
    try:
        file_paths = ["examples/resources/image.jpg"]
        prompt = "Describe the images"

        session_id = chat.init_chat_session(stub)

        image_prompt_option = chat.get_prompt_options({'name': 'QueryImagesPrompt'})
        response_iterator = chat.set_chat_request(stub, name='SuperBuilder Python Clients!', prompt=prompt, session_id=session_id, attachments=file_paths, prompt_options=image_prompt_option)
        response = chat.get_chat_response(response_iterator)

        chat.remove_session(stub, session_id)
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
    except Exception as e:
        print(f"Error: {e}")

def workflow_summarize(stub):
    try:
        file_paths = ["examples/resources/Minimum Wages Order 2022.pdf"]
        prompt1 = "Summarize"
        prompt2 = "What is the minimum wages order for 2022 in Malaysia?"

        session_id = chat.init_chat_session(stub)
        prompt_options = chat.get_prompt_options({'name': 'SummarizePrompt'})

        # summarize files
        response_iterator = chat.set_chat_request(stub, prompt1, session_id, attachments=file_paths, prompt_options=prompt_options)
        response = chat.get_chat_response(response_iterator)

        # questions on summarized files
        response_iterator = chat.set_chat_request(stub, prompt2, session_id, attachments=file_paths, prompt_options=prompt_options)
        response = chat.get_chat_response(response_iterator)

        chat.remove_session(stub, session_id)
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
    except Exception as e:
        print(f"Error: {e}")

def workflow_query_tables(stub):
    try:
        file_paths = ["examples/resources/organizations-100.csv"]
        prompt1 = "Describe the table"
        prompt2 = "Which company was founded in 1972?"

        session_id = chat.init_chat_session(stub)
        prompt_options = chat.get_prompt_options({'name': 'QueryTablesPrompt'})

        response_iterator = chat.set_chat_request(stub, prompt1, session_id, attachments=file_paths, prompt_options=prompt_options)
        response = chat.get_chat_response(response_iterator)

        response_iterator = chat.set_chat_request(stub, prompt2, session_id, attachments=file_paths, prompt_options=prompt_options)
        response = chat.get_chat_response(response_iterator)

        chat.remove_session(stub, session_id)
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
    except Exception as e:
        print(f"Error: {e}")

def workflow_score_resumes(stub):
    try:
        file_paths = ["examples/resources/Mercy Baker - Resume.pdf",
                     "examples/resources/John Doe - Resume.docx",
                     "examples/resources/Rajesh Krishnan - Resume.docx"]
        job_description = "Cloud engineer with a devOps background and more than 5 years of experience"
        prompt = 'Where did Mercy Baker study?'

        session_id = chat.init_chat_session(stub)

        # score resumes
        prompt_options = chat.get_prompt_options({'name': 'ScoreResumesPrompt', 'is_scoring_criteria': True})
        response_iterator = chat.set_chat_request(stub, job_description, session_id, attachments=file_paths, prompt_options=prompt_options)
        response = chat.get_chat_response(response_iterator)

        # questions on resumes
        prompt_options = chat.get_prompt_options({'name': 'ScoreResumesPrompt', 'is_scoring_criteria': False})
        response_iterator = chat.set_chat_request(stub, prompt, session_id, attachments=file_paths, prompt_options=prompt_options)
        response = chat.get_chat_response(response_iterator)

        # this workflow adds files to the knowledge base
        rag.remove_uploaded_file(stub, file_paths)
        chat.remove_session(stub, session_id)
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
    except Exception as e:
        print(f"Error: {e}")

def workflow_score_documents(stub):
    try:
        file_paths = ["examples/resources/Mercy Baker - Resume.pdf",
                     "examples/resources/John Doe - Resume.docx",
                     "examples/resources/Rajesh Krishnan - Resume.docx"]
        evaluation_criteria = "Evaluate how well the resume matches the job description: Cloud engineer with a devOps background and more than 5 years of experience"
        prompt = 'Where did Mercy Baker study?'

        session_id = chat.init_chat_session(stub)

        # score documents
        prompt_options = chat.get_prompt_options({'name': 'ScoreDocumentsPrompt', 'is_scoring_criteria': True, 'include_reasoning': True})
        response_iterator = chat.set_chat_request(stub, evaluation_criteria, session_id, attachments=file_paths, prompt_options=prompt_options)
        response = chat.get_chat_response(response_iterator)

        # questions on documents
        prompt_options = chat.get_prompt_options({'name': 'ScoreDocumentsPrompt', 'is_scoring_criteria': False})
        response_iterator = chat.set_chat_request(stub, prompt, session_id, attachments=file_paths, prompt_options=prompt_options)
        response = chat.get_chat_response(response_iterator)

        chat.remove_session(stub, session_id)
    except grpc.RpcError as e:
        print(f"gRPC error: {e.details()}")
    except Exception as e:
        print(f"Error: {e}")
