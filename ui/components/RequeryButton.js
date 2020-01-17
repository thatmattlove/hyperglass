import React from "react";
import { Button, Icon, Spinner, Tooltip } from "@chakra-ui/core";

export default ({ isLoading, requery, bg = "secondary" }) => {
    return (
        <Tooltip hasArrow label="Reload Query" placement="top">
            <Button size="sm" variantColor={bg} zIndex="1" onClick={requery} mx={1}>
                {isLoading ? <Spinner size="sm" /> : <Icon size="16px" name="repeat" />}
            </Button>
        </Tooltip>
    );
};
