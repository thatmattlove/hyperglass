import {
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Skeleton,
  useDisclosure,
} from '@chakra-ui/react';
import 'reactflow/dist/style.css';
import { useBreakpointValue, useColorValue, useFormState } from '~/hooks';
import { Chart } from './chart';
import { PathButton } from './path-button';

interface PathProps {
  device: string;
}

export const Path = (props: PathProps): JSX.Element => {
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
            <Skeleton isLoaded={response != null}>
              <Chart data={output} />
            </Skeleton>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
