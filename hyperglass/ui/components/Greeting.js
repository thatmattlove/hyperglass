import * as React from "react";
import {
    Button,
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
    useColorMode,
    useDisclosure,
} from "@chakra-ui/core";
import MarkDown from "~/components/MarkDown";
import { motion } from "framer-motion";

const bg = { light: "white", dark: "black" };
const color = { light: "black", dark: "white" };

const AnimatedModalContent = motion.custom(ModalContent);
const AnimatedModalOverlay = motion.custom(ModalOverlay);

const Greeting = ({ greetingConfig, content, onClickThrough }) => {
    const { isOpen, onOpen, onClose } = useDisclosure(true);
    const { colorMode } = useColorMode();

    const handleClick = () => {
        onClickThrough(true);
        onClose();
    };

    return (
        <Modal
            onClose={handleClick}
            isOpen={isOpen}
            size="full"
            isCentered
            closeOnOverlayClick={!greetingConfig.required}
        >
            <AnimatedModalOverlay
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3, delay: 0.7 }}
            />
            <AnimatedModalContent
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.3, delay: 0.7 }}
                bg={bg[colorMode]}
                color={color[colorMode]}
                py={4}
                borderRadius="md"
                maxW={["95%", "75%", "75%", "75%"]}
            >
                <ModalHeader>{greetingConfig.title}</ModalHeader>
                {!greetingConfig.required && <ModalCloseButton />}
                <ModalBody>
                    <MarkDown content={content} />
                </ModalBody>
                <ModalFooter>
                    <Button variantColor="primary" onClick={handleClick}>
                        {greetingConfig.button}
                    </Button>
                </ModalFooter>
            </AnimatedModalContent>
        </Modal>
    );
};

Greeting.displayName = "Greeting";

export default Greeting;
