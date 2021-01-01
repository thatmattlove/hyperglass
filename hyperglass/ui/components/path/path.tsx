import {
  Modal,
  ModalBody,
  ModalHeader,
  ModalOverlay,
  ModalContent,
  useDisclosure,
  Skeleton,
  ModalCloseButton,
} from '@chakra-ui/react';
import { useColorValue } from '~/context';
import { useLGState, useLGMethods } from '~/hooks';
import { PathButton } from './button';
import { Chart } from './chart';

import type { TPath } from './types';

export const Path = (props: TPath) => {
  const { device } = props;
  const { displayTarget } = useLGState();
  const { getResponse } = useLGMethods();
  const { isOpen, onClose, onOpen } = useDisclosure();
  const response = getResponse(device);
  const output = response?.output as TStructuredResponse;
  const bg = useColorValue('whiteSolid.50', 'blackSolid.900');

  return (
    <>
      <PathButton onOpen={onOpen} />
      <Modal isOpen={isOpen} onClose={onClose} size="full" isCentered>
        <ModalOverlay />
        <ModalContent bg={bg} maxW={{ base: '100%', lg: '80%' }} maxH={{ base: '80%', lg: '60%' }}>
          <ModalHeader>{`Path to ${displayTarget.value}`}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {response !== null ? <Chart data={output} /> : <Skeleton w="500px" h="300px" />}
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
