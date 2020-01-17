import React from "react";
import styled from "@emotion/styled";
import { Input, useColorMode, useTheme } from "@chakra-ui/core";

const StyledInput = styled(Input)`
    &::placeholder {
        color: ${props => props.placeholderColor};
    }
`;

export default ({ placeholder, register }) => {
    const theme = useTheme();
    const { colorMode } = useColorMode();
    const bg = colorMode === "dark" ? theme.colors.whiteAlpha[100] : theme.colors.white;
    const color = colorMode === "dark" ? theme.colors.whiteAlpha[800] : theme.colors.gray[400];
    const border = colorMode === "dark" ? theme.colors.whiteAlpha[50] : theme.colors.gray[100];
    const borderRadius = theme.space[1];
    const placeholderColor =
        colorMode === "dark" ? theme.colors.whiteAlpha[400] : theme.colors.gray[400];
    return (
        <StyledInput
            name="query_target"
            ref={register}
            placeholder={placeholder}
            placeholderColor={placeholderColor}
            size="lg"
            bg={bg}
            color={color}
            borderColor={border}
            borderRadius={borderRadius}
        />
    );
};
