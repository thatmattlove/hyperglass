import React from "react";
import { Flex, IconButton } from "@chakra-ui/core";
import styled from "@emotion/styled";
import {
    color,
    ColorProps,
    justifyContent,
    JustifyContentProps,
    space,
    SpaceProps,
} from "styled-system";

export const StyledTable = styled.div`
    ${space};
    flex: 1;
    width: 100%;
    display: flex;
    max-width: 100%;
    overflow-x: auto;
    border-radius: 4px;
    flex-direction: column;
    box-sizing: border-box;
`;

export const TableHead = styled.div`
    ${space};
    display: flex;
    flex-direction: row;
`;

export const TableCell = styled("div")`
    ${space};
    ${color};
    ${justifyContent};
    flex: 1;
    display: flex;
    min-width: 150px;
    align-items: center;
    border-bottom-width: 1px;
    overflow: hidden;
    text-overflow: ellipsis;
`;

export const TableRow = styled(Flex)`
    &:hover {
        cursor: pointer;
        background-color: rgba(0, 0, 0, 0.01);
    }
`;

export const TableIconButton = ({ icon, onClick, isDisabled, children, variantColor, ...rest }) => {
    return (
        <IconButton
            size="sm"
            {...rest}
            icon={icon}
            borderWidth={1}
            onClick={onClick}
            variantColor={variantColor}
            isDisabled={isDisabled}
            aria-label="Table Icon button"
        >
            {children}
        </IconButton>
    );
};

TableIconButton.defaultProps = {
    variantColor: "gray",
};
