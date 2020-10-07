import * as React from 'react';
import {
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Stack,
  Tag,
  useDisclosure,
  useColorMode,
  useTheme,
} from '@chakra-ui/core';
import { useConfig, useMedia } from 'app/context';
import { CodeBlock } from 'app/components';

const prettyMediaSize = {
  sm: 'SMALL',
  md: 'MEDIUM',
  lg: 'LARGE',
  xl: 'X-LARGE',
};

export const Debugger = () => {
  const { isOpen: configOpen, onOpen: onConfigOpen, onClose: configClose } = useDisclosure();
  const { isOpen: themeOpen, onOpen: onThemeOpen, onClose: themeClose } = useDisclosure();
  const config = useConfig();
  const theme = useTheme();
  const bg = { light: 'white', dark: 'black' };
  const color = { light: 'black', dark: 'white' };
  const { colorMode } = useColorMode();
  const { mediaSize } = useMedia();
  const borderColor = { light: 'gray.100', dark: 'gray.600' };
  return (
    <>
      <Stack
        borderWidth="1px"
        borderColor={borderColor[colorMode]}
        py={4}
        px={4}
        isInline
        position="relative"
        left={0}
        right={0}
        bottom={0}
        justifyContent="center"
        zIndex={1000}
        maxW="100%">
        <Tag variantColor="gray">{colorMode.toUpperCase()}</Tag>
        <Tag variantColor="teal">{prettyMediaSize[mediaSize]}</Tag>
        <Button size="sm" variantColor="cyan" onClick={onConfigOpen}>
          View Config
        </Button>
        <Button size="sm" variantColor="purple" onClick={onThemeOpen}>
          View Theme
        </Button>
      </Stack>
      <Modal isOpen={configOpen} onClose={configClose} size="full">
        <ModalOverlay />
        <ModalContent
          bg={bg[colorMode]}
          color={color[colorMode]}
          py={4}
          borderRadius="md"
          maxW="90%">
          <ModalHeader>Loaded Configuration</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <CodeBlock>{JSON.stringify(config, null, 4)}</CodeBlock>
          </ModalBody>
        </ModalContent>
      </Modal>
      <Modal isOpen={themeOpen} onClose={themeClose} size="full">
        <ModalOverlay />
        <ModalContent
          bg={bg[colorMode]}
          color={color[colorMode]}
          py={4}
          borderRadius="md"
          maxW="90%">
          <ModalHeader>Loaded Theme</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <CodeBlock>{JSON.stringify(theme, null, 4)}</CodeBlock>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
