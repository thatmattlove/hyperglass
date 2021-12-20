import { Modal, ModalBody, ModalOverlay, ModalContent, ModalCloseButton } from '@chakra-ui/react';
import { useColorValue } from '~/hooks';

import type { PromptProps } from './types';

export const MobilePrompt = (props: PromptProps): JSX.Element => {
  const { children, trigger, ...disclosure } = props;
  const bg = useColorValue('white', 'gray.900');
  return (
    <>
      {trigger}
      <Modal
        size="xs"
        isCentered
        closeOnEsc={false}
        closeOnOverlayClick={false}
        motionPreset="slideInBottom"
        {...disclosure}
      >
        <ModalOverlay />
        <ModalContent bg={bg}>
          <ModalCloseButton />
          <ModalBody px={4} py={10}>
            {children}
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
