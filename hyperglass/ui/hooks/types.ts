import type { QueryFunctionContext } from 'react-query';
import type { TFormQuery } from '~/types';

export interface TOpposingOptions {
  light?: string;
  dark?: string;
}

export type TUseGreetingReturn = [boolean, (v?: boolean) => void];

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
