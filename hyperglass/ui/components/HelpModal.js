import * as React from 'react';
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
  useTheme,
} from '@chakra-ui/core';
import { motion, AnimatePresence } from 'framer-motion';
import { Markdown } from 'app/components';

const AnimatedIcon = motion.custom(IconButton);

export const HelpModal = ({ item, name }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { colors } = useTheme();
  const { colorMode } = useColorMode();
  const bg = { light: 'whiteFaded.50', dark: 'blackFaded.800' };
  const color = { light: 'black', dark: 'white' };
  const iconColor = {
    light: colors.primary[500],
    dark: colors.primary[300],
  };
  return (
    <>
      <AnimatePresence>
        <AnimatedIcon
          initial={{ opacity: 0, scale: 0.3, color: colors.gray[500] }}
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
            <Markdown content={item.content} />
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
