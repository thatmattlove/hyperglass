import type { FlexProps } from '@chakra-ui/react';

export interface ICardBody extends Omit<FlexProps, 'onClick'> {
  onClick?: () => boolean;
}

export interface ICardFooter extends FlexProps {}

export interface ICardHeader extends FlexProps {}
