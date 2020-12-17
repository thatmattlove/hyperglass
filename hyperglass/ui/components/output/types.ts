import type { BoxProps, FlexProps, TextProps } from '@chakra-ui/react';
import type { TCellRender } from '~/types';

export interface TTextOutput extends Omit<BoxProps, 'children'> {
  children: string;
}

export interface TActive {
  isActive: boolean;
}

export interface TMonoField extends TextProps {
  v: React.ReactNode;
}

export interface TAge extends TextProps {
  inSeconds: number;
}

export interface TWeight extends TextProps {
  weight: number;
  winningWeight: 'low' | 'high';
}

export interface TASPath {
  path: number[];
  active: boolean;
}

export interface TCommunities {
  communities: string[];
}

export interface TRPKIState {
  state:
    | 0 // Invalid
    | 1 // Valid
    | 2 // Unknown
    | 3; // Unverified
  active: boolean;
}

export interface TCell {
  data: TCellRender;
  rawData: TStructuredResponse;
}

export interface TBGPTable extends Omit<FlexProps, 'children'> {
  children: TStructuredResponse;
}
