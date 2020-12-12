import type { MenuListProps } from '@chakra-ui/react';

type TFooterSide = 'left' | 'right';

export interface TFooterButton extends Omit<MenuListProps, 'title'> {
  side: TFooterSide;
  title?: MenuListProps['children'];
  content: string;
}

export type TFooterItems = 'help' | 'credit' | 'terms';
