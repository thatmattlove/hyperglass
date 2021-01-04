import dynamic from 'next/dynamic';
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
import { Markdown } from '~/components';
import { useColorValue } from '~/context';
import { isQueryContent } from '~/types';

import type { THelpModal } from './types';

const Info = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiInfo));

export const HelpModal: React.FC<THelpModal> = (props: THelpModal) => {
  const { visible, item, name, ...rest } = props;
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bg = useColorValue('whiteSolid.50', 'blackSolid.800');
  const color = useColorValue('black', 'white');
  if (!isQueryContent(item)) {
    return null;
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
          icon={<Info />}
          onClick={onOpen}
          colorScheme="blue"
          aria-label={`${name}_help`}
        />
      </ScaleFade>
      <Modal isOpen={isOpen} onClose={onClose} size="xl" motionPreset="slideInRight">
        <ModalOverlay />
        <ModalContent bg={bg} color={color} py={4} borderRadius="md" {...rest}>
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
