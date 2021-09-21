import {
  Tag,
  Modal,
  HStack,
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
import { HiOutlineDownload as RefreshIcon } from '@meronex/icons/hi';
import { IosColorPalette as ThemeIcon } from '@meronex/icons/ios';
import { MdcCodeJson as ConfigIcon } from '@meronex/icons/mdc';
import { useConfig, useColorValue, useBreakpointValue } from '~/context';
import { CodeBlock } from '~/components';
import { useHyperglassConfig } from '~/hooks';

import type { UseDisclosureReturn } from '@chakra-ui/react';

interface TViewer extends Pick<UseDisclosureReturn, 'isOpen' | 'onClose'> {
  title: string;
  children: React.ReactNode;
}

const Viewer: React.FC<TViewer> = (props: TViewer) => {
  const { title, isOpen, onClose, children } = props;
  const bg = useColorValue('white', 'blackSolid.700');
  const color = useColorValue('black', 'white');
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="full" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent bg={bg} color={color} py={4} borderRadius="md" maxW="90%" minH="90vh">
        <ModalHeader>{title}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <CodeBlock>{children}</CodeBlock>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export const Debugger: React.FC = () => {
  const { isOpen: configOpen, onOpen: onConfigOpen, onClose: configClose } = useDisclosure();
  const { isOpen: themeOpen, onOpen: onThemeOpen, onClose: themeClose } = useDisclosure();
  const { colorMode } = useColorMode();
  const config = useConfig();
  const theme = useTheme();
  const borderColor = useColorValue('gray.100', 'gray.600');
  const mediaSize =
    useBreakpointValue({ base: 'SMALL', md: 'MEDIUM', lg: 'LARGE', xl: 'X-LARGE' }) ?? 'UNKNOWN';
  const tagSize = useBreakpointValue({ base: 'sm', lg: 'lg' }) ?? 'lg';
  const btnSize = useBreakpointValue({ base: 'xs', lg: 'sm' }) ?? 'sm';
  const { refetch } = useHyperglassConfig();
  return (
    <>
      <HStack
        py={4}
        px={4}
        left={0}
        right={0}
        bottom={0}
        maxW="100%"
        zIndex={1000}
        borderWidth="1px"
        position="relative"
        justifyContent="center"
        borderColor={borderColor}
        spacing={{ base: 2, lg: 8 }}
      >
        <Tag size={tagSize} colorScheme="gray">
          {colorMode.toUpperCase()}
        </Tag>
        <Button size={btnSize} leftIcon={<ConfigIcon />} colorScheme="cyan" onClick={onConfigOpen}>
          View Config
        </Button>
        <Button size={btnSize} leftIcon={<ThemeIcon />} colorScheme="blue" onClick={onThemeOpen}>
          View Theme
        </Button>
        <Button
          size={btnSize}
          colorScheme="purple"
          leftIcon={<RefreshIcon />}
          onClick={() => refetch()}
        >
          Reload Config
        </Button>
        <Tag size={tagSize} colorScheme="teal">
          {mediaSize}
        </Tag>
      </HStack>
      <Viewer isOpen={configOpen} onClose={configClose} title="Config">
        {JSON.stringify(config, null, 4)}
      </Viewer>
      <Viewer isOpen={themeOpen} onClose={themeClose} title="Theme">
        {JSON.stringify(theme, null, 4)}
      </Viewer>
    </>
  );
};
