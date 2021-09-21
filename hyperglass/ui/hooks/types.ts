import type { UseQueryOptions } from 'react-query';
import type * as ReactGA from 'react-ga';
import type { Device, TFormQuery } from '~/types';

export type LGQueryKey = [string, TFormQuery];
export type DNSQueryKey = [string, { target: string | null; family: 4 | 6 }];

export type LGQueryOptions = Omit<
  UseQueryOptions<QueryResponse, Response | QueryResponse | Error, QueryResponse, LGQueryKey>,
  | 'queryKey'
  | 'queryFn'
  | 'cacheTime'
  | 'refetchOnWindowFocus'
  | 'refetchInterval'
  | 'refetchOnMount'
>;

export interface TOpposingOptions {
  light?: string;
  dark?: string;
}

export interface UseGreeting {
  isAck: boolean;
  isOpen: boolean;
  greetingReady: boolean;
  ack(value: boolean): void;
  open(): void;
  close(): void;
}

export type TUseDevice = (
  /**
   * Device's ID, e.g. the device.name field.
   */
  deviceId: string,
) => Device;

export type UseStrfArgs = { [k: string]: unknown } | string;

export type TTableToStringFormatter =
  | ((v: string) => string)
  | ((v: number) => string)
  | ((v: number[]) => string)
  | ((v: string[]) => string)
  | ((v: boolean) => string);

export type TTableToStringFormatted = {
  age: (v: number) => string;
  active: (v: boolean) => string;
  as_path: (v: number[]) => string;
  communities: (v: string[]) => string;
  rpki_state: (v: number, n: RPKIState) => string;
};

export type GAEffect = (ga: typeof ReactGA) => void;

export interface GAReturn {
  ga: typeof ReactGA;
  initialize(trackingId: string | null, debug: boolean): void;
  trackPage(path: string): void;
  trackModal(path: string): void;
  trackEvent(event: ReactGA.EventArgs): void;
}
