import React from "react";
import {
    IconButton,
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalBody,
    ModalCloseButton,
    useDisclosure,
    useColorMode,
    useTheme
} from "@chakra-ui/core";
import { motion, AnimatePresence } from "framer-motion";
import MarkDown from "~/components/MarkDown";

const AnimatedIcon = motion.custom(IconButton);

export default ({ item, name }) => {
    const { isOpen, onOpen, onClose } = useDisclosure();
    const theme = useTheme();
    const { colorMode } = useColorMode();
    const bg = { light: theme.colors.white, dark: theme.colors.dark };
    const color = { light: theme.colors.black, dark: theme.colors.white };
    const iconColor = { light: theme.colors.primary[500], dark: theme.colors.primary[300] };
    return (
        <>
            <AnimatePresence>
                <AnimatedIcon
                    initial={{ opacity: 0, scale: 0.3, color: theme.colors.gray[500] }}
                    animate={{ opacity: 1, scale: 1, color: iconColor[colorMode] }}
                    transition={{ duration: 0.2 }}
                    exit={{ opacity: 0, scale: 0.3 }}
                    variantColor="primary"
                    aria-label={`${name}_help`}
                    icon="info-outline"
                    variant="link"
                    size="sm"
                    h="unset"
                    w={3}
                    minW={3}
                    maxW={3}
                    h={3}
                    minH={3}
                    maxH={3}
                    ml={1}
                    mb={1}
                    onClick={onOpen}
                />
            </AnimatePresence>
            <Modal isOpen={isOpen} onClose={onClose} size="xl">
                <ModalOverlay />
                <ModalContent bg={bg[colorMode]} color={color[colorMode]} py={4} borderRadius="md">
                    <ModalHeader>{item.params.title}</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <MarkDown content={item.content} />
                    </ModalBody>
                </ModalContent>
            </Modal>
        </>
    );
};
