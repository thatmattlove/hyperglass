import type { ButtonProps, DrawerProps, DrawerContentProps } from '@chakra-ui/react';

type TFooterSide = 'left' | 'right';

export interface TFooterButton extends ButtonProps {
  side: TFooterSide;
  href?: string;
}

export interface TFooterContent extends Omit<DrawerProps, 'children'>, DrawerContentProps {
  isOpen: boolean;
  content: string;
  side: TFooterSide;
}

export type TFooterItems = 'help' | 'credit' | 'terms';
