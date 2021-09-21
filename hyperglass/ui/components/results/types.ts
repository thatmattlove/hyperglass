import type { ButtonProps } from '@chakra-ui/react';
import type { UseQueryResult } from 'react-query';

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

export interface ResultProps {
  index: number;
  queryLocation: string;
}

export type TErrorLevels = 'success' | 'warning' | 'error';

export interface TCopyButton extends ButtonProps {
  copyValue: string;
}

export interface TRequeryButton extends ButtonProps {
  requery: UseQueryResult<QueryResponse>['refetch'];
}
