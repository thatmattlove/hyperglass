import type { IconButtonProps } from '@chakra-ui/react';

export type SubmitButtonProps = Omit<IconButtonProps, 'aria-label'>;

export interface ResponsiveSubmitButtonProps {
  isOpen: boolean;
  onClose(): void;
  children: React.ReactNode;
}
