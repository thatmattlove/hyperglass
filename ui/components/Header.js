import React from "react";
import { Flex, IconButton, useColorMode, useTheme } from "@chakra-ui/core";
import { motion } from "framer-motion";

const AnimatedFlex = motion.custom(Flex);

export default () => {
    const theme = useTheme();
    const { colorMode, toggleColorMode } = useColorMode();
    const bg = { light: theme.colors.white, dark: theme.colors.black };
    const icon = { light: "moon", dark: "sun" };
    return (
        <Flex
            position="fixed"
            as="header"
            top="0"
            zIndex="4"
            bg={bg[colorMode]}
            color={theme.colors.gray[500]}
            left="0"
            right="0"
            width="full"
            height="4rem"
        >
            <Flex w="100%" mx="auto" px={6} justifyContent="flex-end">
                <AnimatedFlex
                    align="center"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.6 }}
                >
                    <IconButton
                        aria-label={`Switch to ${colorMode === "light" ? "dark" : "light"} mode`}
                        variant="ghost"
                        color="current"
                        ml="2"
                        fontSize="20px"
                        onClick={toggleColorMode}
                        icon={icon[colorMode]}
                    />
                </AnimatedFlex>
            </Flex>
        </Flex>
    );
};
