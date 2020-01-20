import React from "react";
import { Flex, useColorMode, useTheme } from "@chakra-ui/core";

export default React.forwardRef(
    ({ value, label, labelColor, valueBg, valueColor, ...props }, ref) => {
        const theme = useTheme();
        const { colorMode } = useColorMode();
        const _labelColor = { dark: "whiteAlpha.700", light: "blackAlpha.700" };
        const _valueBg = { light: theme.colors.primary[600], dark: theme.colors.primary[600] };
        const _valueColor = { light: "white", dark: "white" };
        return (
            <Flex
                ref={ref}
                flexWrap="nowrap"
                alignItems="center"
                justifyContent="flex-start"
                mx={[1, 2, 2, 2]}
                my={2}
                {...props}
            >
                <Flex
                    display="inline-flex"
                    justifyContent="center"
                    lineHeight="1.5"
                    px={[1, 3, 3, 3]}
                    whiteSpace="nowrap"
                    mb={2}
                    mr={0}
                    bg={valueBg || _valueBg[colorMode]}
                    color={valueColor || _valueColor[colorMode]}
                    borderBottomLeftRadius={4}
                    borderTopLeftRadius={4}
                    borderBottomRightRadius={0}
                    borderTopRightRadius={0}
                    fontWeight="bold"
                    fontSize={["xs", "sm", "sm", "sm"]}
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
                    boxShadow={`inset 0px 0px 0px 1px ${valueBg || _valueBg[colorMode]}`}
                    color={labelColor || _labelColor[colorMode]}
                    borderBottomRightRadius={4}
                    borderTopRightRadius={4}
                    borderBottomLeftRadius={0}
                    borderTopLeftRadius={0}
                    fontSize={["xs", "sm", "sm", "sm"]}
                >
                    {label}
                </Flex>
            </Flex>
        );
    }
);
