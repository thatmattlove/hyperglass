import type { FlexProps, ButtonProps, CollapseProps } from '@chakra-ui/core';

type TFooterSide = 'left' | 'right';

export interface IFooterButton extends ButtonProps {
  side: TFooterSide;
  href?: string;
}

export interface IFooterContent extends Omit<CollapseProps, 'children'> {
  isOpen: boolean;
  content: string;
  side: TFooterSide;
  children?: undefined;
}

export type TFooterItems = 'help' | 'credit' | 'terms';
