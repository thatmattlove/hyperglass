import { FlexProps } from '@chakra-ui/react';

export interface TLabel extends FlexProps {
  value: string;
  label: string;
  bg: string;
  valueColor?: string;
  labelColor?: string;
}
