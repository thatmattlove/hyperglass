import type { BoxProps, ButtonProps } from '@chakra-ui/react';

export interface TCopyButton extends ButtonProps {
  copyValue: string;
}

export interface TColorModeToggle extends ButtonProps {
  size?: string;
}
export type TButtonSizeMap = {
  xs: BoxProps;
  sm: BoxProps;
  md: BoxProps;
  lg: BoxProps;
};

export interface TSubmitButton extends BoxProps {
  isLoading: boolean;
  isDisabled: boolean;
  isActive: boolean;
  isFullWidth: boolean;
  size: keyof TButtonSizeMap;
  loadingText: string;
}

export interface TRequeryButton extends ButtonProps {
  requery(): void;
}
