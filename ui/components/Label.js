import React from "react";
import { Flex, useColorMode, useTheme } from "@chakra-ui/core";

export default React.forwardRef(
    ({ value, label, labelBg, labelColor, valueBg, valueColor }, ref) => {
        const theme = useTheme();
        const { colorMode } = useColorMode();
        const _labelBg = { light: theme.colors.black, dark: theme.colors.gray[200] };
        const _labelColor = { light: theme.colors.white, dark: theme.colors.white };
        const _valueBg = { light: theme.colors.primary[600], dark: theme.colors.primary[600] };
        const _valueColor = { light: theme.colors.white, dark: theme.colors.white };
        return (
            <Flex ref={ref} flexWrap="wrap" alignItems="center" justifyContent="flex-start" mx={2}>
                <Flex
                    display="inline-flex"
                    justifyContent="center"
                    lineHeight="1.5"
                    px={3}
                    whiteSpace="nowrap"
                    mb={2}
                    mr={0}
                    bg={valueBg || _valueBg[colorMode]}
                    color={valueColor || _valueColor[colorMode]}
                    borderBottomLeftRadius={4}
                    borderTopLeftRadius={4}
                    borderBottomRightRadius={0}
                    borderTopRightRadius={0}
                    fontSize="sm"
                    fontWeight="bold"
                >
                    {value}
                </Flex>
                <Flex
                    display="inline-flex"
                    justifyContent="center"
                    lineHeight="1.5"
                    px={3}
                    whiteSpace="nowrap"
                    mb={2}
                    ml={0}
                    mr={0}
                    bg={labelBg || _labelBg[colorMode]}
                    color={labelColor || _labelColor[colorMode]}
                    borderBottomRightRadius={4}
                    borderTopRightRadius={4}
                    borderBottomLeftRadius={0}
                    borderTopLeftRadius={0}
                    fontSize="sm"
                >
                    {label}
                </Flex>
            </Flex>
        );
    }
);
