import type { ModalContentProps } from '@chakra-ui/react';
import type { QueryContent } from '~/types';

export interface THelpModal extends ModalContentProps {
  item: QueryContent | null;
  name: string;
  visible: boolean;
}
