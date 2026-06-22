import "../WorkflowGlobalStyles.css";
import React, { useState, useEffect } from "react";
import ActiveFileView from "../../fileManagement/ActiveFileView";
import Chat from "../../chat/Chat";
import { WorkflowContainer } from "../WorkflowGlobalStyles";

const WorkflowTable = ({loading}) => {
    const [attachedFiles, setAttachedFiles] = useState([]);
    const [ attachedFilesVisible, setAttachedFilesVisible ] = useState(true);
    const onActiveFileChange = (newAttachedFiles) => { setAttachedFiles(newAttachedFiles); };
    const selectedFileLimit = 3;
    return (
        <WorkflowContainer>
            <ActiveFileView
                expanded={attachedFilesVisible}
                setExpanded={setAttachedFilesVisible}
                onSelectionChange={onActiveFileChange}
                allowedFileTypes={["xlsx", "csv"]}
                selectedFileLimit={selectedFileLimit}
                fileInstructionsText={`Add or select up to ${selectedFileLimit} files`}
                uploadType="QueryTables" // tell backend to only store filepaths, no embeddings
            />
            <Chat
                readyToChat={attachedFiles.length > 0}
                defaultValue="Describe the tables"
                queryType="QueryTables"
                onMessageSend={() => setAttachedFilesVisible(false)}
                onResubmitSend={() => setAttachedFilesVisible(false)}
                activeFiles={attachedFiles}
            />
        </WorkflowContainer>
    )
};
export default WorkflowTable;