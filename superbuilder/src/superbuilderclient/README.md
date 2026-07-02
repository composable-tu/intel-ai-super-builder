# Frontend client 
The frontend client is built with Tauri + React + Typescript

## Recommended IDE Setup
- [VS Code](https://code.visualstudio.com/)
- [Tauri](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode)
- [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer)

## Build instructions
To build the frontend client, follow these steps: 
1. Setup Development Environment
   - Install Tauri [pre requisites](https://tauri.app/v1/guides/getting-started/prerequisites)
2. Install local pre-requisites
   ```
   cd superbuilderclient
   npm install
   ```
3. Install mui/material for React.Js
      - Follow this link [guide](https://mui.com/material-ui/)
4. Install Protoc. There are two options: 
   - You can follow the instructions from [here](https://grpc.io/docs/protoc-installation/)  
   - If you are running on a Windows based machine, you only have this option:
      - Go to the [latest release](https://github.com/protocolbuffers/protobuf/releases/latest) and download the binary
      - Add this environment variable
         ```
         PROTOC=\path\to\protoc-<ver>-win64\bin\protoc.exe
         ```
5. Build Service (Middleware) proto
   - Tauri will automatically build the proto contract files when you run dev or build mode. The definition is in the `build.rs` file. 
   - Inside `build.rs`, it goes to the a shared folder looking for `superbuilder_middleware.proto`. 
6. To run the application locally, run 
   ```
   npm run tauri dev
   ```
7. To build the application locally, run 
   ```
   npm run tauri build
   ```
## Developer information

Some icons are rendered using SVG files. An easy way to change the color of an SVG icon is to use a hexadecimal color to CSS filter converter.
https://isotropic.co/tool/hex-color-to-css-filter/ , using this you can apply a css style to the svg component to alter the color. 
(You may need to manually adjust brightness of the output filter to get the desired results)

## Setup Support Account
To configure Bug report support email account you can either directly set that in the code or set an environment variable. 
For Windows system, 
* Open System Properties (Win + R, type sysdm.cpl)
* Click "Environment Variables"
* Under "System variables", click "New"
* Set Variable name: VITE_AAB_SUPPORT_EMAIL
* Set Variable value: your-support@company.com
* Click OK