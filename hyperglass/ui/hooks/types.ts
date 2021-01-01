import { State } from '@hookstate/core';
import type { QueryFunctionContext } from 'react-query';
import type { TFormQuery } from '~/types';

export interface TOpposingOptions {
  light?: string;
  dark?: string;
}

export type TUseGreetingReturn = {
  ack: State<boolean>;
  isOpen: State<boolean>;
  open(): void;
  close(): void;
  greetingReady(): boolean;
};

export interface TUseLGQueryFn {
  pageParam?: QueryFunctionContext['pageParam'];
  queryKey: [string, TFormQuery];
}

export interface TUseASNDetailFn {
  pageParam?: QueryFunctionContext['pageParam'];
  queryKey: string;
}

interface TUseDNSQueryParams {
  target: string;
  family: 4 | 6;
}

export interface TUseDNSQueryFn {
  pageParam?: QueryFunctionContext['pageParam'];
  queryKey: [string | null, TUseDNSQueryParams];
}
