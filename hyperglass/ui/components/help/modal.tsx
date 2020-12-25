import dynamic from 'next/dynamic';
import {
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
} from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';
import { Markdown } from '~/components';
import { useColorValue } from '~/context';

import type { THelpModal } from './types';

const Info = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiInfo));

export const HelpModal = (props: THelpModal) => {
  const { item, name, ...rest } = props;
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bg = useColorValue('whiteFaded.50', 'blackFaded.800');
  const color = useColorValue('black', 'white');
  return (
    <>
      <AnimatePresence>
        <motion.div
          transition={{ duration: 0.2 }}
          exit={{ opacity: 0, scale: 0.3 }}
          animate={{ opacity: 1, scale: 1 }}
          initial={{ opacity: 0, scale: 0.3 }}>
          <IconButton
            mb={1}
            ml={1}
            minH={3}
            minW={3}
            size="md"
            variant="link"
            icon={<Info />}
            onClick={onOpen}
            colorScheme="blue"
            aria-label={`${name}_help`}
          />
        </motion.div>
      </AnimatePresence>
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent bg={bg} color={color} py={4} borderRadius="md" {...rest}>
          <ModalHeader>{item.params.title}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Markdown content={item.content} />
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
