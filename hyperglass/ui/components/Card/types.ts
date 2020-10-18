import type { FlexProps } from '@chakra-ui/core';

export interface ICardBody extends Omit<FlexProps, 'onClick'> {
  onClick?: () => boolean;
}
