import * as React from "react";
import { useTheme } from "@chakra-ui/core";

const LightningBolt = ({ size = 4, color = "currentColor" }) => {
    const theme = useTheme();
    return (
        <svg
            width={theme.space[size]}
            height={theme.space[size]}
            viewBox="0 0 16 16"
            fill={theme.colors[color]}
            xmlns="http://www.w3.org/2000/svg"
        >
            <path
                fillRule="evenodd"
                d="M11.251.068a.5.5 0 0 1 .227.58L9.677 6.5H13a.5.5 0 0 1 .364.843l-8 8.5a.5.5 0 0 1-.842-.49L6.323 9.5H3a.5.5 0 0 1-.364-.843l8-8.5a.5.5 0 0 1 .615-.09z"
                clipRule="evenodd"
            />
        </svg>
    );
};

LightningBolt.displayName = "LightningBolt";

export default LightningBolt;
