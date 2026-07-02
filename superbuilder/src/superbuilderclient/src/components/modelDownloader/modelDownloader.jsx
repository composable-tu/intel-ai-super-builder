import React, { useEffect, useState, useRef } from "react";
import "./modelDownloader.css";
import DownloadBody from "./DownloadBody";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { Button, Icon } from "@mui/material";
import { useContext } from "react";
import { ModelDownloaderContext } from "../context/ModelDownloaderContext";

import useDataStore from "../../stores/DataStore";
import { useTranslation } from 'react-i18next';

const ModelDownloader = () => {
  const { config, assistant, setAssistant, setConfig } = useDataStore();
  const [downloadStatus, setDownloadStatus] = useState("Nothing to download!");
  const hasDownloadedRef = useRef(false);
  const modelStatusesRef = useRef([]);
  const [modelStatuses, setModelStatuses] = useState([]);
  const [fileDownload, setFileDownload] = useState("");
  const [progress, setProgress] = useState(0);
  const {
    isInitDownload,
    setDownloadInProgress,
    downloadData,
    setDownloadData,
    downloadConsent,
    setDownloadConsent,
    waitingForConsent,
    downloadWindowsOpen,
    setDownloadWindowsOpen,
    setDownloadFailed,
    pendingModelSelection,
    setPendingModelSelection,
    removeModelsFromUrl,
    resetDownloadState,
  } = useContext(ModelDownloaderContext);

  useEffect(() => {
    const unlisten = listen("download-progress", (event) => {
      const [downloadFile, progressData] = event.payload;
      setFileDownload(downloadFile);
      setProgress(progressData);
    });

    return () => {
      unlisten.then((fn) => fn());
    };
  }, []);

  useEffect(() => {
    if (isInitDownload && downloadData && !hasDownloadedRef.current) {
      setDownloadWindowsOpen(true);
      downloadFiles();
    }
  }, [isInitDownload]);

  useEffect(() => {
    if (assistant?.models) {
      setModelStatuses(
        Object.entries(assistant.models).map(([modelType, modelName]) => ({
          modelType,
          modelName,
          statusMessage: "Ready",
        }))
      );
      // Save the new object into modelStatusesRef.current
      modelStatusesRef.current = Object.entries(assistant.models).map(
        ([modelType, modelName]) => ({
          modelType,
          modelName,
          statusMessage: "Ready",
        })
      );
    }

  }, [assistant]);

  useEffect(() => {
    if (
      downloadData?.missing_models?.length > 0 &&
      downloadConsent === true &&
      waitingForConsent === false
    ) {
      downloadFiles();
    } else if (
      downloadData?.missing_models?.length > 0 &&
      downloadConsent === false &&
      waitingForConsent === true
    ) {
      setDownloadStatus("Awaiting consent to download models");
    }
  }, [downloadData?.missing_models, downloadConsent, waitingForConsent]);

  useEffect(() => {
    if (
      downloadStatus === "Awaiting consent to download models" &&
      downloadData?.missing_models?.length > 0 &&
      downloadConsent === false &&
      waitingForConsent === true
    ) {
      setDownloadWindowsOpen(true);
    }
  }, [downloadStatus, downloadData?.missing_models, downloadConsent, waitingForConsent]);

  const applyPendingModelSelection = () => {
    if (!pendingModelSelection) {
      return;
    }

    const updatedAssistant = {
      ...assistant,
      models: {
        ...assistant.models,
        [pendingModelSelection.modelType]: pendingModelSelection.modelName,
      },
    };
    setAssistant(updatedAssistant);
    setConfig({
      ...config,
      ActiveAssistant: updatedAssistant,
    });
    setPendingModelSelection(null);
  };

  const updateModelStatus = (modelName, newStatusMessage) => {
    console.log(modelName, newStatusMessage);
    console.log(modelStatusesRef.current);
    if (modelStatusesRef.current.length === 0) {
      const updatedStatuses = modelStatuses.map((item) => {
        if (item.modelName === modelName) {
          return { ...item, statusMessage: newStatusMessage };
        }
        return item;
      });
      setModelStatuses(updatedStatuses);
      modelStatusesRef.current = updatedStatuses;
    } else {
      const updatedStatuses = modelStatusesRef.current.map((item) => {
        if (item.modelName === modelName) {
          return { ...item, statusMessage: newStatusMessage };
        }
        return item;
      });
      setModelStatuses(updatedStatuses);
      modelStatusesRef.current = updatedStatuses;
    }
  };

  const downloadFiles = async () => {
    try {
      // Clear any prior failure and rebuild statuses fresh for this attempt
      setDownloadFailed(false);
      setDownloadInProgress(true);
      setDownloadStatus("Downloading");
      const activeStatuses = Object.entries(assistant.models).map(([modelType, modelName]) => ({
        modelType,
        modelName,
        statusMessage: downloadData.missing_models.includes(modelName) ? "Downloading" : "Ready",
      }));
      const activeModelNames = new Set(activeStatuses.map(({ modelName }) => modelName));
      const pendingStatuses = downloadData.missing_models
        .filter((modelName) => !activeModelNames.has(modelName))
        .map((modelName) => {
          const model = assistant.all_models.find((entry) => entry.full_name === modelName);
          return {
            modelType:
              pendingModelSelection?.modelName === modelName
                ? pendingModelSelection.modelType
                : model?.model_type || "model",
            modelName,
            statusMessage: "Downloading",
          };
        });
      const freshStatuses = [...activeStatuses, ...pendingStatuses];
      setModelStatuses(freshStatuses);
      modelStatusesRef.current = freshStatuses;

      console.log("invoking download file, ", downloadData);
      const downloadPromises = downloadData.missing_models.map((filename) => {
        const model = assistant.all_models.find(
          (model) => model.full_name === filename
        );
        let fileUrl = model ? model.download_link : null;
        if (fileUrl) {
          try {
            const urlObj = new URL(fileUrl);
            const basePath = `${urlObj.protocol}//${urlObj.host}`;
            if (basePath !== "https://aibuilder.intel.com") {
              const modelEndpointObj = new URL(config.download_endpoint);
              urlObj.protocol = modelEndpointObj.protocol;
              urlObj.host = modelEndpointObj.host;
              fileUrl = urlObj.toString();
              fileUrl = removeModelsFromUrl(fileUrl)
            }
          } catch (error) {
            console.error("Invalid URL:", error);
            return Promise.reject(new Error(`Invalid URL for model ${filename}`));
          }
        }
        console.log("Download model ", model, "from url: ", fileUrl);
        const newPath = `${downloadData.models_dir_path}${filename}`;
        return invoke("download_file", {
          fileUrl: fileUrl,
          localPath: newPath,
        });
      });

      const results = await Promise.allSettled(downloadPromises);
      results.forEach((result, index) => {
        const modelName = downloadData.missing_models[index];
        const statusMessage =
          result.status === "fulfilled"
            ? result.value.includes("Error")
              ? `Not available ${result.value}`
              : "Ready"
            : `Failed ${result.reason}`;
        updateModelStatus(modelName, statusMessage);
      });

      // Check if any statusMessage is not "Ready"
      const hasError = modelStatusesRef.current.some(
        (status) => status.statusMessage !== "Ready"
      );

      console.log("hasError", hasError, modelStatusesRef.current);
      if (hasError) {
        throw new Error("One or more models failed to download.");
      }
      hasDownloadedRef.current = true;
      applyPendingModelSelection();
      resetDownloadState({ clearData: true, clearFailure: true });
      setDownloadStatus("All downloads complete");
    } catch (error) {
      console.error("Error downloading files:", error);
      setDownloadStatus("Downloads incomplete");
      resetDownloadState();
      setDownloadFailed(true);
    }
  };

  const canRenderDownloaderModal =
    downloadWindowsOpen &&
    (downloadStatus !== "Awaiting consent to download models" ||
      (downloadData?.missing_models?.length > 0 && downloadConsent === false));

  return (
    <>
      {
        canRenderDownloaderModal && (
          <div className="modal-overlay">
            <div
              className="downloader-container modal-content"
              onClick={(e) => e.stopPropagation()}
              data-testid="model-downloader-modal"
            >
              <DownloadHeader />
              <DownloadBody
                downloadStatus={downloadStatus}
                setDownloadStatus={setDownloadStatus}
                fileDownload={fileDownload}
                progress={progress}
                modelStatuses={modelStatusesRef.current}
              />
            </div>
          </div>
        )
      }
    </>
  );
};

const DownloadHeader = () => {
  const { t } = useTranslation();
  return (
  <div className="download-header">
    <p>
      <span className="p-large">{t('model_downloader.head.part_1')}</span>
      <span className="p-small">
        {" "}
        {t('model_downloader.head.part_2')}
      </span>
    </p>
  </div>
);
}

export default ModelDownloader;
