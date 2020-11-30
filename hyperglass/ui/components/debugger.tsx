import {
  Tag,
  Modal,
  Stack,
  Button,
  useTheme,
  ModalBody,
  ModalHeader,
  ModalOverlay,
  ModalContent,
  useColorMode,
  useDisclosure,
  ModalCloseButton,
} from '@chakra-ui/react';
import { useConfig, useColorValue, useBreakpointValue } from '~/context';
import { CodeBlock } from '~/components';

export const Debugger = () => {
  const { isOpen: configOpen, onOpen: onConfigOpen, onClose: configClose } = useDisclosure();
  const { isOpen: themeOpen, onOpen: onThemeOpen, onClose: themeClose } = useDisclosure();
  const { colorMode } = useColorMode();
  const config = useConfig();
  const theme = useTheme();
  const bg = useColorValue('white', 'black');
  const color = useColorValue('black', 'white');
  const borderColor = useColorValue('gray.100', 'gray.600');
  const mediaSize =
    useBreakpointValue({ base: 'SMALL', md: 'MEDIUM', lg: 'LARGE', xl: 'X-LARGE' }) ?? 'UNKNOWN';
  return (
    <>
      <Stack
        py={4}
        px={4}
        isInline
        left={0}
        right={0}
        bottom={0}
        maxW="100%"
        zIndex={1000}
        borderWidth="1px"
        position="relative"
        justifyContent="center"
        borderColor={borderColor}>
        <Tag variantColor="gray">{colorMode.toUpperCase()}</Tag>
        <Tag variantColor="teal">{mediaSize}</Tag>
        <Button size="sm" variantColor="cyan" onClick={onConfigOpen}>
          View Config
        </Button>
        <Button size="sm" variantColor="purple" onClick={onThemeOpen}>
          View Theme
        </Button>
      </Stack>
      <Modal isOpen={configOpen} onClose={configClose} size="full">
        <ModalOverlay />
        <ModalContent bg={bg} color={color} py={4} borderRadius="md" maxW="90%">
          <ModalHeader>Loaded Configuration</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <CodeBlock>{JSON.stringify(config, null, 4)}</CodeBlock>
          </ModalBody>
        </ModalContent>
      </Modal>
      <Modal isOpen={themeOpen} onClose={themeClose} size="full">
        <ModalOverlay />
        <ModalContent bg={bg} color={color} py={4} borderRadius="md" maxW="90%">
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
