import React from "react";
import { Flex, IconButton, useColorMode } from "@chakra-ui/core";
import { motion, AnimatePresence } from "framer-motion";
import ResetButton from "~/components/ResetButton";
import useMedia from "~/components/MediaProvider";
import Title from "~/components/Title";

const AnimatedFlex = motion.custom(Flex);
const AnimatedResetButton = motion.custom(ResetButton);

const titleVariants = {
    sm: {
        fullSize: { scale: 1, marginLeft: 0 },
        small: { marginLeft: "auto" }
    },
    md: {
        fullSize: { scale: 1 },
        small: { scale: 1 }
    },
    lg: {
        fullSize: { scale: 1 },
        small: { scale: 1 }
    },
    xl: {
        fullSize: { scale: 1 },
        small: { scale: 1 }
    }
};

const icon = { light: "moon", dark: "sun" };
const bg = { light: "white", dark: "black" };
const colorSwitch = { dark: "Switch to light mode", light: "Switch to dark mode" };
const headerTransition = { type: "spring", ease: "anticipate", damping: 15, stiffness: 100 };

export default ({ height, isSubmitting, handleFormReset, ...props }) => {
    const { colorMode, toggleColorMode } = useColorMode();
    const { mediaSize } = useMedia();
    const resetButton = (
        <AnimatePresence key="resetButton">
            <AnimatedFlex
                layoutTransition={headerTransition}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0, width: "unset" }}
                exit={{ opacity: 0, x: -50 }}
                alignItems="center"
                mb={[null, "auto"]}
            >
                <AnimatedResetButton isSubmitting={isSubmitting} onClick={handleFormReset} />
            </AnimatedFlex>
        </AnimatePresence>
    );
    const title = (
        <AnimatedFlex
            key="title"
            px={1}
            alignItems={isSubmitting ? "center" : ["center", "center", "flex-end", "flex-end"]}
            positionTransition={headerTransition}
            initial={{ scale: 0.5 }}
            animate={isSubmitting ? "small" : "fullSize"}
            variants={titleVariants[mediaSize]}
            justifyContent="center"
            mb={[null, isSubmitting ? "auto" : null]}
            mt={[null, isSubmitting ? null : "auto"]}
            maxW="100%"
            flex="1 0 0"
        >
            <Title isSubmitting={isSubmitting} onClick={handleFormReset} />
        </AnimatedFlex>
    );
    const colorModeToggle = (
        <AnimatedFlex
            layoutTransition={headerTransition}
            key="colorModeToggle"
            alignItems="center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            mb={[null, "auto"]}
        >
            <IconButton
                aria-label={colorSwitch[colorMode]}
                variant="ghost"
                color="current"
                ml={2}
                pl={0}
                fontSize="20px"
                onClick={toggleColorMode}
                icon={icon[colorMode]}
            />
        </AnimatedFlex>
    );
    const layout = {
        false: {
            sm: [title, resetButton, colorModeToggle],
            md: [resetButton, title, colorModeToggle],
            lg: [resetButton, title, colorModeToggle],
            xl: [resetButton, title, colorModeToggle]
        },
        true: {
            sm: [resetButton, colorModeToggle, title],
            md: [resetButton, title, colorModeToggle],
            lg: [resetButton, title, colorModeToggle],
            xl: [resetButton, title, colorModeToggle]
        }
    };
    return (
        <Flex
            px={2}
            top="0"
            left="0"
            right="0"
            zIndex="4"
            as="header"
            width="full"
            flex="1 0 auto"
            position="fixed"
            bg={bg[colorMode]}
            color="gray.500"
            height={height}
            {...props}
        >
            <Flex w="100%" mx="auto" py={6} justify="space-between" alignItems="center">
                {layout[isSubmitting][mediaSize]}
            </Flex>
        </Flex>
    );
};
