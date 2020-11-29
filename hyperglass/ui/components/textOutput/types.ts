import type { BoxProps } from '@chakra-ui/react';

export interface TTextOutput extends Omit<BoxProps, 'children'> {
  children: string;
}
