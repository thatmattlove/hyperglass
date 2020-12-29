import type { ModalContentProps } from '@chakra-ui/react';
import type { TQueryContent, TQueryFields } from '~/types';

export interface THelpModal extends ModalContentProps {
  item: TQueryContent | null;
  name: TQueryFields;
  visible: boolean;
}
