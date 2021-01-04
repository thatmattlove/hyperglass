import type { FlexProps } from '@chakra-ui/react';

export interface TCardBody extends Omit<FlexProps, 'onClick'> {
  onClick?: () => boolean;
}

export interface TCardFooter extends FlexProps {}

export interface TCardHeader extends FlexProps {}
