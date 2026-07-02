## Python integration example

* Install latest SuperBuilder

* Install Python 3.12.9 
https://www.python.org/downloads/release/python-3129/

* How to install
  * Double click on file "install.bat"

* How to launch
  * Double click on file "run.bat"

* How to test
  * Double click on file "run_tests.bat"


## Generate python proto file
`python -m grpc_tools.protoc -I ../../SuperBuilderService/Protos --python_out=. --grpc_python_out=. ../../SuperBuilderService/Protos/greet.proto
`