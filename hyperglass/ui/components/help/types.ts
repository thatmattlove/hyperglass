import type { ModalContentProps } from '@chakra-ui/react';

export interface THelpModal extends Omit<ModalContentProps, 'title'> {
  title: string | null;
  item: string | null;
  name: string;
  visible: boolean;
}
