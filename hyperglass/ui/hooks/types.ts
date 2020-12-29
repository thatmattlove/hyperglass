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
