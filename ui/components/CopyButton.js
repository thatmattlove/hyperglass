import React from "react";
import { Button, Icon, Tooltip, useClipboard } from "@chakra-ui/core";

export default ({ bg = "secondary", copyValue }) => {
    const { onCopy, hasCopied } = useClipboard(copyValue);
    return (
        <Tooltip hasArrow label="Copy Output" placement="top">
            <Button size="sm" variantColor={bg} zIndex="1" onClick={onCopy} mx={1}>
                {hasCopied ? <Icon name="check" size="16px" /> : <Icon name="copy" size="16px" />}
            </Button>
        </Tooltip>
    );
};
