import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  CircularProgress,
} from "@mui/material";
import { Circle } from "@mui/icons-material";
import ModalWrapper from "../generalUseModal/generalUseModal";
import useDataStore from "../../stores/DataStore";
import { invoke } from "@tauri-apps/api/core";
import { useState } from "react";
import { useTranslation } from "react-i18next";

const CommitIdAlert = ({ isOpen }) => {
  const { t } = useTranslation();
  const { commitIdValidation } = useDataStore();
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState("");

  // Show dialog only if there are orphaned models
  if (!commitIdValidation.orphanedModels?.length > 0) {
    return null;
  }

  const handleAutoRemove = async () => {
    setIsProcessing(true);
    setProcessingStep(t("model_incompatible.preparing_remove_models"));

    try {
      let allSuccessful = true;
      let failedModels = [];

      // Remove each model using the existing remove_model command
      for (let i = 0; i < commitIdValidation.orphanedModels.length; i++) {
        const modelName = commitIdValidation.orphanedModels[i];

        // Update processing step to show current model being removed
        setProcessingStep(
          t("model_incompatible.removing_model", {
            modelName,
            current: i + 1,
            total: commitIdValidation.orphanedModels.length,
          })
        );

        try {
          await invoke("remove_model", {
            modelName: modelName,
            isIncompatibleModelRemoval: true,
          });
          console.log(`Successfully removed model: ${modelName}`);
        } catch (error) {
          console.error(`Failed to remove model ${modelName}:`, error);
          allSuccessful = false;
          failedModels.push(modelName);
        }
      }

      if (allSuccessful) {
        // All models removed successfully - clear validation and reload immediately
        useDataStore.getState().clearCommitIdValidation();
        setProcessingStep(t("model_incompatible.remove_models_success"));

        // Small delay to show the success message, then reload
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      } else {
        // Some models failed - show error and stop processing
        setIsProcessing(false);
        alert(
          t("model_incompatible.remove_models_failed", {
            failedModels: failedModels.join(", "),
          })
        );
      }
    } catch (error) {
      console.error("Failed to remove incompatible models:", error);
      setIsProcessing(false);
      alert(
        t("model_incompatible.remove_models_failed_generic") +
          "\n\n" +
          t("model_incompatible.remove_models_error", {
            error: error.message,
          })
      );
    }
  };

  // Custom footer content
  const footerContent = (
    <div className={"info-footer"}>
      <Button
        className="footer-button"
        variant="contained"
        sx={{ borderRadius: "0px" }}
        onClick={handleAutoRemove}
        disabled={isProcessing}
        startIcon={isProcessing ? <CircularProgress size={16} /> : null}
      >
        {isProcessing
          ? `${processingStep}`
          : t("model_incompatible.button_remove_models")}
      </Button>
    </div>
  );

  // Show main dialog
  return (
    <ModalWrapper
      isOpen={isOpen}
      header={t("model_incompatible.header_model_updates_required")}
      footerContent={footerContent}
    >
      <Box>
        <Typography>
          {t("model_incompatible.incompatible_models_message")}
        </Typography>

        {/* Models list */}
        <Box>
          <List>
            {commitIdValidation.orphanedModels.map((modelName) => (
              <ListItem key={modelName} sx={{ py: 0 }}>
                <ListItemIcon sx={{ minWidth: 20 }}>
                  <Circle sx={{ fontSize: 8 }} />
                </ListItemIcon>
                <ListItemText primary={modelName} />
              </ListItem>
            ))}
          </List>
        </Box>
      </Box>
    </ModalWrapper>
  );
};

export default CommitIdAlert;
