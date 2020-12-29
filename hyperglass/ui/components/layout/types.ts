import type { FlexProps } from '@chakra-ui/react';

export interface TFrame extends FlexProps {}

export interface TResetButton extends FlexProps {
  developerMode: boolean;
  resetForm(): void;
}
