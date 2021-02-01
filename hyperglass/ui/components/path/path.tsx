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
import { useLGState, useLGMethods } from '~/hooks';
import { PathButton } from './button';
import { Chart } from './chart';

import type { TPath } from './types';

export const Path: React.FC<TPath> = (props: TPath) => {
  const { device } = props;
  const { displayTarget } = useLGState();
  const { getResponse } = useLGMethods();
  const { isOpen, onClose, onOpen } = useDisclosure();
  const response = getResponse(device);
  const output = response?.output as TStructuredResponse;
  const bg = useColorValue('light.50', 'dark.900');
  const centered = useBreakpointValue({ base: false, lg: true }) ?? true;
  return (
    <>
      <PathButton onOpen={onOpen} />
      <Modal isOpen={isOpen} onClose={onClose} size="full" isCentered={centered}>
        <ModalOverlay />
        <ModalContent
          bg={bg}
          mt={{ base: 4, lg: '' }}
          maxH={{ base: '80%', lg: '60%' }}
          maxW={{ base: '100%', lg: '80%' }}
        >
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
