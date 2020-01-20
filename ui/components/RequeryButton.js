import React from "react";
import { Button, Icon, Tooltip } from "@chakra-ui/core";

export default ({ requery, bg = "secondary", ...props }) => {
    return (
        <Tooltip hasArrow label="Reload Query" placement="top">
            <Button
                as="a"
                size="sm"
                variantColor={bg}
                zIndex="1"
                onClick={requery}
                mx={1}
                {...props}
            >
                <Icon size="16px" name="repeat" />
            </Button>
        </Tooltip>
    );
};
