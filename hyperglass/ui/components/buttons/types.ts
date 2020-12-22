import type { IconButtonProps, ButtonProps } from '@chakra-ui/react';
import type { OnChangeArgs } from '~/types';

export interface TCopyButton extends ButtonProps {
  copyValue: string;
}

export interface TColorModeToggle extends ButtonProps {
  size?: string;
}

export interface TSubmitButton extends Omit<IconButtonProps, 'aria-label'> {
  handleChange(e: OnChangeArgs): void;
}

export interface TRequeryButton extends ButtonProps {
  requery(): void;
}

export interface TRSubmitButton {
  isOpen: boolean;
  onClose(): void;
  onChange(e: OnChangeArgs): void;
  children: React.ReactNode;
}

export interface TPathButton {
  onOpen(): void;
}
