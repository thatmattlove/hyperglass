import type { ButtonProps, FlexProps } from '@chakra-ui/react';
import type { UseQueryResult } from 'react-query';
import type { TDevice, TQueryTypes } from '~/types';

export interface TResultHeader {
  title: string;
  loading: boolean;
  isError?: boolean;
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
  queryVrf: string;
  queryTarget: string;
  queryLocation: string;
  queryType: TQueryTypes;
  resultsComplete: number[];
  setComplete: React.Dispatch<React.SetStateAction<number[]>>;
}

export type TErrorLevels = 'success' | 'warning' | 'error';

export interface TCopyButton extends ButtonProps {
  copyValue: string;
}

export interface TRequeryButton extends ButtonProps {
  requery: UseQueryResult<TQueryResponse>['refetch'];
}
