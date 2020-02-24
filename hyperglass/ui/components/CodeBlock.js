import React from "react";
import { Box, useColorMode, useTheme } from "@chakra-ui/core";

export default ({ children }) => {
    const { colorMode } = useColorMode();
    const theme = useTheme();
    const bg = { dark: theme.colors.gray[800], light: theme.colors.blackAlpha[100] };
    const color = { dark: theme.colors.white, light: theme.colors.black };
    return (
        <Box
            fontFamily="mono"
            mt={5}
            p={3}
            border="1px"
            borderColor="inherit"
            rounded="md"
            bg={bg[colorMode]}
            color={color[colorMode]}
            fontSize="sm"
            whiteSpace="pre-wrap"
            as="pre"
        >
            {children}
        </Box>
    );
};
