import {
  Modal,
  Skeleton,
  ModalBody,
  ModalHeader,
  ModalOverlay,
  ModalContent,
  useDisclosure,
  ModalCloseButton,
} from '@chakra-ui/react';
import { useColorValue, useBreakpointValue } from '~/context';
import { useFormState } from '~/hooks';
import { PathButton } from './button';
import { Chart } from './chart';

import type { TPath } from './types';

export const Path = (props: TPath): JSX.Element => {
  const { device } = props;
  const displayTarget = useFormState(s => s.target.display);
  const getResponse = useFormState(s => s.response);
  const { isOpen, onClose, onOpen } = useDisclosure();
  const response = getResponse(device);
  const output = response?.output as StructuredResponse;
  const bg = useColorValue('light.50', 'dark.900');
  const centered = useBreakpointValue({ base: false, lg: true }) ?? true;
  return (
    <>
      <PathButton onOpen={onOpen} />
      <Modal isOpen={isOpen} onClose={onClose} size="full" isCentered={centered}>
        <ModalOverlay />
        <ModalContent
          bg={bg}
          minH={{ lg: '80vh' }}
          maxH={{ base: '80%', lg: '60%' }}
          maxW={{ base: '100%', lg: '80%' }}
        >
          <ModalHeader>{`Path to ${displayTarget}`}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {response !== null ? <Chart data={output} /> : <Skeleton w="500px" h="300px" />}
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
