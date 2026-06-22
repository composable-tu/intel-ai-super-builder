import React, { useState, useEffect, useContext, useRef } from "react";
import "./LightTooltip.css";
import Tooltip, { tooltipClasses } from "@mui/material/Tooltip";
import { styled } from "@mui/material/styles";
import Zoom from "@mui/material/Zoom";
import { Switch } from "@mui/material";

const LightTooltip = styled(
      ({ className, placement = "top-start", ...props }) => (
        <Tooltip
          {...props}
          arrow
          placement={placement}
          classes={{ popper: className }}
          slots={{ transition: Zoom }}
        />
      )
    )(({ theme }) => ({
      [`& .${tooltipClasses.tooltip}`]: {
        backgroundColor: "rgba(238, 238, 238, 0.87)",
        color: "rgba(0, 0, 0, 0.87)",
        boxShadow: theme.shadows[1],
        fontSize: 11,
      },
}));

export default LightTooltip;