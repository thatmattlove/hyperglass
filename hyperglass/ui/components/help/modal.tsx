import {
  Modal,
  ScaleFade,
  ModalBody,
  IconButton,
  ModalHeader,
  ModalOverlay,
  ModalContent,
  useDisclosure,
  ModalCloseButton,
} from '@chakra-ui/react';
import { DynamicIcon, Markdown } from '~/components';
import { useColorValue } from '~/context';

import type { THelpModal } from './types';

export const HelpModal = (props: THelpModal): JSX.Element => {
  const { visible, item, name, title, ...rest } = props;
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bg = useColorValue('whiteSolid.50', 'blackSolid.800');
  const color = useColorValue('black', 'white');
  if (item === null) {
    return <></>;
  }
  return (
    <>
      <ScaleFade in={visible} unmountOnExit>
        <IconButton
          mb={1}
          ml={1}
          minH={3}
          minW={3}
          size="md"
          variant="link"
          onClick={onOpen}
          colorScheme="blue"
          aria-label={`${name}_help`}
          icon={<DynamicIcon icon={{ fi: 'FiInfo' }} />}
        />
      </ScaleFade>
      <Modal isOpen={isOpen} onClose={onClose} size="xl" motionPreset="slideInRight">
        <ModalOverlay />
        <ModalContent bg={bg} color={color} py={4} borderRadius="md" {...rest}>
          <ModalHeader>{title}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Markdown content={item} />
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
