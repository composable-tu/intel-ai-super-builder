if (-not [Environment]::GetEnvironmentVariable('PROTOC'))
{
    "Environment PROTOC is not configured"
    "check scripts/README.md on how to fix this"
    exit 1
}

$root_dir="$PSScriptRoot\\.." | Resolve-Path
$proto_dir="$root_dir\\example\\proto"

# recompile proto for python
"csharp automatically recompile proto when build"
""
""
# recompile proto for golang
"recompile proto for golang"
$golang_dir="$root_dir\\example\\golang"
$golang_proto_dir="$golang_dir\\proto"
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
& $env:PROTOC -I $proto_dir --go_opt=paths=source_relative --go-grpc_opt=paths=source_relative --go_out=$golang_proto_dir --go-grpc_out=$golang_proto_dir $proto_dir\\superbuilder_service.proto
""
""
# recompile proto for python
"recompile proto for python"
$python_dir="$root_dir\\example\\python"
python -m pip install grpcio-tools
python -m grpc_tools.protoc -I $proto_dir --python_out=$python_dir --grpc_python_out=$python_dir $proto_dir\\superbuilder_service.proto
""
""