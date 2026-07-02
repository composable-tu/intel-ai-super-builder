package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"math/rand"

	middleware "superbuilder/proto"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func main() {
	serverAddress := "localhost:5006"
	fmt.Println("connecting to server at", serverAddress)

	conn, err := grpc.NewClient(serverAddress, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()

	// middlewareClient responsible for communicating with the server
	middlewareClient := middleware.NewSuperBuilderClient(conn)

	// create longer context to manage the connection timeout
	// this is to compensate for the long running functions, e.g. SetParameters
	ctx_no_timeout := context.Context(context.Background())

	// ------------------ example of calling server ------------------

	// example 1 - call server and return system information
	fmt.Println("\n\nexample 1 - call server and return system information")
	fmt.Println("==========")
	responseSayHello, err := middlewareClient.SayHello(ctx_no_timeout, &middleware.SayHelloRequest{})
	if err != nil {
		log.Fatalf("error calling function SayHello: %v", err)
	}
	fmt.Println(responseSayHello.GetMessage())

	// example 2 - call server and return chat history
	fmt.Println("\n\nexample 2 - call server and return chat history")
	fmt.Println("==========")
	responseGetChatHistory, err := middlewareClient.GetChatHistory(ctx_no_timeout, &middleware.GetChatHistoryRequest{})
	if err != nil {
		log.Fatalf("error calling function GetChatHistory: %v", err)
	}
	fmt.Println(responseGetChatHistory.GetData())

	// example 3 - get current client model configuration
	fmt.Println("\n\nexample 3 - call server and return client model configuration")
	fmt.Println("==========")
	responseGetClientConfig, err := middlewareClient.GetClientConfig(ctx_no_timeout, &middleware.GetClientConfigRequest{})
	if err != nil {
		log.Fatalf("error calling function GetClientConfig: %v", err)
	}
	fmt.Println(responseGetClientConfig.GetData())

	// unmarshal json
	var f interface{}
	err = json.Unmarshal([]byte(responseGetClientConfig.Data), &f)
	if err != nil {
		log.Fatalf("error unmarshalling client config: %v", err)
	}

	currentUserConfig := f.(map[string]interface{})
	ActiveAssistant := currentUserConfig["ActiveAssistant"].(map[string]interface{})
	selectedModels := ActiveAssistant["models"]
	AllModels := ActiveAssistant["all_models"].([]interface{})

	fmt.Println("\n\nAvailable models:")

	for _, each := range AllModels {
		current := each.(map[string]interface{})
		model := fmt.Sprintf("[%s] %s", current["model_type"], current["full_name"])
		fmt.Println(model)
	}
	fmt.Println("")

	// show activeAssistant Model configuration
	var embedding_model map[string]interface{}
	var ranker_model map[string]interface{}
	var chat_model map[string]interface{}

	for _, each := range selectedModels.([]interface{}) {
		current := each.(map[string]interface{})
		if current["model_type"] == "chat_model" {
			chat_model = current
		}
		if current["model_type"] == "embedding_model" {
			embedding_model = current
		}
		if current["model_type"] == "ranker_model" {
			ranker_model = current
		}
	}
	fmt.Println("current embedding model:", embedding_model["full_name"])
	fmt.Println("current ranker model:", ranker_model["full_name"])
	fmt.Println("current chat model:", chat_model["full_name"])

	// example 4 - change active chat model
	fmt.Println("\n\nexample 4 - Set active assistant")
	fmt.Println("==========")

	var newModelsConfiguration []map[string]interface{}
	newModelsConfiguration = append(newModelsConfiguration, embedding_model)
	newModelsConfiguration = append(newModelsConfiguration, ranker_model)
	newModelsConfiguration = append(newModelsConfiguration, chat_model)

	ModelsJsonFormat, err := json.Marshal(newModelsConfiguration)
	if err != nil {
		log.Fatalf("error marshalling new models configuration: %v", err)
	}
	responseSetActiveAssistant, err := middlewareClient.SetActiveAssistant(ctx_no_timeout, &middleware.SetActiveAssistantRequest{
		Assistant:  ActiveAssistant["short_name"].(string),
		ModelsJson: string(ModelsJsonFormat),
	})
	if err != nil {
		log.Fatalf("error calling function SetActiveAssistant: %v", err)
	}
	fmt.Println(responseSetActiveAssistant)

	// example 5 - load models into memory
	fmt.Println("\n\nexample 5 - load models into memory")
	fmt.Println("==========")
	responseSayHelloPyllm, err := middlewareClient.SayHelloPyllm(ctx_no_timeout, &middleware.SayHelloRequest{})
	if err != nil {
		log.Fatalf("error calling function SayHelloPyllm: %v", err)
	}
	fmt.Println("is backend ready: " + responseSayHelloPyllm.Message)

	responseLoadModels, err := middlewareClient.LoadModels(ctx_no_timeout, &middleware.LoadModelsRequest{})
	if err != nil {
		log.Fatalf("error calling function LoadModels: %v", err)
	}
	fmt.Println("is model loaded:", responseLoadModels.Status)

	if !responseLoadModels.Status {
		log.Fatalf("error loading models: %v", responseLoadModels.Status)
	}

	// example 6 - chat with the server
	fmt.Println("\n\nexample 6 - chat with the server")
	fmt.Println("==========")

	var questions []string = []string{
		"hi there",
		"why the sky blue?",
		"why the sea purple?",
		"why the tree leaf green?",
	}

	middlewareChatRequest := middleware.ChatRequest{
		Name:   "SuperBuilder Go Clients!",
		Prompt: questions[rand.Intn(len(questions))],
	}

	fmt.Println("Question:\n", middlewareChatRequest.Prompt)
	responseHandler, err := middlewareClient.Chat(ctx_no_timeout, &middlewareChatRequest)
	if err != nil {
		log.Fatalf("error calling function Chat: %v", err)
	}

	fullMessage := ""
	for {
		chatResponse, err := responseHandler.Recv()
		if err == io.EOF {
			// End of stream reached
			break
		} else if err != nil {
			log.Fatalf("error receiving chat response: %v", err)
		} else {
			messageObject := chatResponse.GetMessage()
			fullMessage += messageObject
			fmt.Print(messageObject)
		}

	}

	// example 7  - Add MCP Server and MCP Agent
	fmt.Println("\n\nexample 7 - Add MCP Server and MCP Agent")
	fmt.Println("==========")

	// Add MCP Server
	mcpServer := middleware.MCPServer{
		ServerName: "ExampleMCPServer",
		Command:    "",
		Args:       "", // Example port
		Url:        "http://127.0.0.1:7905/sse",
		Env:        "",
	}
	mcpServerRequest := &middleware.AddMCPServerRequest{
		Server: &mcpServer,
	}

	resultAddMCPServer, err := middlewareClient.AddMCPServer(ctx_no_timeout, mcpServerRequest)
	if err != nil {
		log.Fatalf("error calling function AddMCPServer: %v", err)
	}
	fmt.Println("AddMCPServer response:")
	fmt.Println(resultAddMCPServer)

	// Get MCP Servers
	resultGetMCPServers, err := middlewareClient.GetMCPServers(ctx_no_timeout, &middleware.GetMCPServersRequest{})
	if err != nil {
		log.Fatalf("error calling function GetMCPServers: %v", err)
	}
	fmt.Println("GetMCPServers response:")

	var idForMCPAgent []int32
	for _, item := range resultGetMCPServers.Servers {
		fmt.Printf("MCPServerItem: %+v\n", item)
		idForMCPAgent = append(idForMCPAgent, item.Id)
	}

	// Add MCP Agent
	mcpAgent := &middleware.MCPAgent{
		ServerIds: idForMCPAgent, // Example MCP Server IDs
		Name:      "ExampleAgent",
		Message:   "ExampleType",
		Desc:      "This is an example MCP agent",
	}

	mcpAgentRequest := &middleware.AddMCPAgentRequest{
		Agent: mcpAgent,
	}

	resultAddMCPAgent, err := middlewareClient.AddMCPAgent(ctx_no_timeout, mcpAgentRequest)
	if err != nil {
		log.Fatalf("error calling function AddMCPAgent: %v", err)
	}
	fmt.Println("AddMCPAgent response:")
	fmt.Println(resultAddMCPAgent)

	mcpAgentToRemove := &middleware.RemoveMCPAgentRequest{
		AgentName: "ExampleAgent",
	}

	mcpAgentRequest.Agent.Desc = "Updated description for ExampleAgent"

	// Edit MCP Agent
	resultEditMCPAgent, err := middlewareClient.EditMCPAgent(ctx_no_timeout, (*middleware.EditMCPAgentRequest)(mcpAgentRequest))
	if err != nil {
		log.Fatalf("error calling function EditMCPAgent: %v", err)
	}
	fmt.Println("EditMCPAgent response:")
	fmt.Println(resultEditMCPAgent)

	resultGetMCPAgents, err := middlewareClient.GetMCPAgents(ctx_no_timeout, &middleware.GetMCPAgentsRequest{})
	if err != nil {
		log.Fatalf("error calling function GetMCPAgents: %v", err)
	}
	fmt.Println("GetMCPAgents response:")
	fmt.Println(resultGetMCPAgents)

	// Remove MCP Agent
	resultRemoveMCPAgent, err := middlewareClient.RemoveMCPAgent(ctx_no_timeout, mcpAgentToRemove)
	if err != nil {
		log.Fatalf("error calling function RemoveMCPAgent: %v", err)
	}
	fmt.Println("RemoveMCPAgent response:")
	fmt.Println(resultRemoveMCPAgent)

	fmt.Println("\n\n\n### Golang example ended ###")
}
