import type { ButtonProps, LinkProps, MenuListProps } from '@chakra-ui/react';
import type { TLink, TMenu } from '~/types';

type TFooterSide = 'left' | 'right';

export interface TFooterButton extends Omit<MenuListProps, 'title'> {
  side: TFooterSide;
  title?: MenuListProps['children'];
  content: string;
}

export type TFooterLink = ButtonProps & LinkProps & { title: string };

export type TFooterItems = 'help' | 'credit' | 'terms';

export interface TColorModeToggle extends ButtonProps {
  size?: string;
}

export function isLink(item: TLink | TMenu): item is TLink {
  return 'url' in item;
}

export function isMenu(item: TLink | TMenu): item is TMenu {
  return 'content' in item;
}
