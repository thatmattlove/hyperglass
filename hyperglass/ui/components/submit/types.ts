import type { IconButtonProps } from '@chakra-ui/react';
import type { OnChangeArgs } from '~/types';

export interface TSubmitButton extends Omit<IconButtonProps, 'aria-label'> {
  handleChange(e: OnChangeArgs): void;
}

export interface TRSubmitButton {
  isOpen: boolean;
  onClose(): void;
  onChange(e: OnChangeArgs): void;
  children: React.ReactNode;
}
