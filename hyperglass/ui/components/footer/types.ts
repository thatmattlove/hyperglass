import type { ButtonProps, LinkProps, MenuListProps } from '@chakra-ui/react';
import type { Link, Menu } from '~/types';

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

export function isLink(item: Link | Menu): item is Link {
  return 'url' in item;
}

export function isMenu(item: Link | Menu): item is Menu {
  return 'content' in item;
}
