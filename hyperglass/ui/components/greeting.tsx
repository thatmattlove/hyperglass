import { useEffect } from 'react';
import {
  Modal,
  Button,
  ModalBody,
  ModalHeader,
  ModalFooter,
  ModalOverlay,
  ModalContent,
  ModalCloseButton,
} from '@chakra-ui/react';
import { If, Then } from 'react-if';
import { Markdown } from '~/elements';
import { useConfig } from '~/context';
import { useGreeting, useColorValue, useOpposingColor } from '~/hooks';

import type { ModalContentProps } from '@chakra-ui/react';

export const Greeting = (props: ModalContentProps): JSX.Element => {
  const { web, content } = useConfig();
  const { isAck, isOpen, open, ack } = useGreeting();

  const bg = useColorValue('white', 'gray.800');
  const color = useOpposingColor(bg);

  useEffect(() => {
    if (!web.greeting.enable && !web.greeting.required) {
      ack(true, false);
    }
    if (!isAck && web.greeting.enable) {
      open();
    }
  }, [isAck, open, web.greeting.enable, web.greeting.required, ack]);
  return (
    <Modal
      size="lg"
      isCentered
      onClose={() => ack(false, web.greeting.required)}
      isOpen={isOpen}
      motionPreset="slideInBottom"
      closeOnEsc={web.greeting.required}
      closeOnOverlayClick={web.greeting.required}
    >
      <ModalOverlay />
      <ModalContent
        py={4}
        bg={bg}
        color={color}
        borderRadius="md"
        maxW={{ base: '95%', md: '75%' }}
        {...props}
      >
        <ModalHeader>{web.greeting.title}</ModalHeader>
        <If condition={!web.greeting.required}>
          <Then>
            <ModalCloseButton />
          </Then>
        </If>
        <ModalBody>
          <Markdown content={content.greeting} />
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="primary" onClick={() => ack(true, web.greeting.required)}>
            {web.greeting.button}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
