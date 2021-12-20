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
import { DynamicIcon, Markdown } from '~/elements';
import { useColorValue } from '~/hooks';

import type { ModalContentProps } from '@chakra-ui/react';

interface DirectiveInfoModalProps extends Omit<ModalContentProps, 'title'> {
  title: string | null;
  item: string | null;
  name: string;
  visible: boolean;
}

export const DirectiveInfoModal = (props: DirectiveInfoModalProps): JSX.Element => {
  const { visible, item, name, title, ...rest } = props;
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bg = useColorValue('whiteSolid.50', 'blackSolid.700');
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
          aria-label={`${title} Details`}
          icon={<DynamicIcon icon={{ fa: 'InfoCircle' }} />}
        />
      </ScaleFade>
      <Modal isOpen={isOpen} onClose={onClose} size="xl" motionPreset="scale">
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
