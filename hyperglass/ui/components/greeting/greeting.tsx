import {
  Modal,
  Button,
  ModalBody,
  ModalHeader,
  ModalFooter,
  ModalOverlay,
  ModalContent,
  useDisclosure,
  ModalCloseButton,
} from '@chakra-ui/react';
import { If, Markdown } from '~/components';
import { useConfig, useColorValue } from '~/context';
import { useGreeting, useOpposingColor } from '~/hooks';

import type { TGreeting } from './types';

export const Greeting = (props: TGreeting) => {
  const { web, content } = useConfig();
  const { isOpen, onClose } = useDisclosure();
  const [greetingAck, setGreetingAck] = useGreeting();

  const bg = useColorValue('white', 'gray.800');
  const color = useOpposingColor(bg);

  function handleClose(ack: boolean = false): void {
    if (web.greeting.required && !greetingAck && !ack) {
      setGreetingAck(false);
    } else if (web.greeting.required && !greetingAck && ack) {
      setGreetingAck();
      onClose();
    } else if (web.greeting.required && greetingAck) {
      onClose();
    } else if (!web.greeting.required) {
      setGreetingAck();
      onClose();
    }
  }
  return (
    <Modal
      size="lg"
      isCentered
      onClose={handleClose}
      motionPreset="slideInBottom"
      closeOnEsc={web.greeting.required}
      isOpen={!greetingAck ? true : isOpen}
      closeOnOverlayClick={web.greeting.required}>
      <ModalOverlay />
      <ModalContent
        py={4}
        bg={bg}
        color={color}
        borderRadius="md"
        maxW={{ base: '95%', md: '75%' }}
        {...props}>
        <ModalHeader>{web.greeting.title}</ModalHeader>
        <If c={!web.greeting.required}>
          <ModalCloseButton />
        </If>
        <ModalBody>
          <Markdown content={content.greeting} />
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="primary" onClick={() => handleClose(true)}>
            {web.greeting.button}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
