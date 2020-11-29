import { BoxProps } from '@chakra-ui/react';

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
