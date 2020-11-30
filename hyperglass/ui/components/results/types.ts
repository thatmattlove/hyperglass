import type { BoxProps, FlexProps } from '@chakra-ui/react';
import type { TDevice, TQueryTypes } from '~/types';

export interface TResultHeader {
  title: string;
  loading: boolean;
  error?: Error;
  errorMsg: string;
  errorLevel: 'success' | 'warning' | 'error';
  runtime: number;
}

export interface TFormattedError {
  keywords: string[];
  message: string;
}

export interface TAccordionHeaderWrapper extends FlexProps {
  hoverBg: FlexProps['bg'];
}

export interface TResult {
  index: number;
  device: TDevice;
  timeout: number;
  queryVrf: string;
  queryType: TQueryTypes;
  queryTarget: string;
  setComplete(v: number | null): void;
  queryLocation: string;
  resultsComplete: number | null;
}

export interface TResults extends BoxProps {
  queryType: TQueryTypes;
  queryLocation: string[];
  queryTarget: string;
  queryVrf: string;
}
