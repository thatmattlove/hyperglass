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

import type { TGreeting } from './types';

export const Greeting = (props: TGreeting) => {
  const { onClickThrough, ...rest } = props;
  const { web, content } = useConfig();
  const { isOpen, onClose } = useDisclosure();

  const bg = useColorValue('white', 'black');
  const color = useColorValue('black', 'white');

  function handleClick(): void {
    onClickThrough();
    onClose();
    return;
  }

  return (
    <Modal
      isCentered
      size="full"
      isOpen={isOpen}
      onClose={handleClick}
      closeOnEsc={!web.greeting.required}
      closeOnOverlayClick={!web.greeting.required}>
      <ModalOverlay />
      <ModalContent
        py={4}
        bg={bg}
        color={color}
        borderRadius="md"
        maxW={{ base: '95%', md: '75%' }}
        {...rest}>
        <ModalHeader>{web.greeting.title}</ModalHeader>
        <If c={!web.greeting.required}>
          <ModalCloseButton />
        </If>
        <ModalBody>
          <Markdown content={content.greeting} />
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="primary" onClick={handleClick}>
            {web.greeting.button}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
