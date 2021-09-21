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
import { If, Markdown } from '~/components';
import { useConfig, useColorValue } from '~/context';
import { useGreeting, useOpposingColor } from '~/hooks';

import type { TGreeting } from './types';

export const Greeting: React.FC<TGreeting> = (props: TGreeting) => {
  const { web, content } = useConfig();
  const { isAck, isOpen, open, ack } = useGreeting();

  const bg = useColorValue('white', 'gray.800');
  const color = useOpposingColor(bg);

  useEffect(() => {
    if (!isAck && web.greeting.enable) {
      open();
    }
  }, [isAck, open, web.greeting.enable]);
  return (
    <Modal
      size="lg"
      isCentered
      onClose={() => ack(false)}
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
        <If c={!web.greeting.required}>
          <ModalCloseButton />
        </If>
        <ModalBody>
          <Markdown content={content.greeting} />
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="primary" onClick={() => ack(true)}>
            {web.greeting.button}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
