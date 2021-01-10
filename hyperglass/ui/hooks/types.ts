import type { State } from '@hookstate/core';
import type { QueryFunctionContext } from 'react-query';
import type * as ReactGA from 'react-ga';
import type {
  TDevice,
  Families,
  TFormQuery,
  TDeviceVrf,
  TQueryTypes,
  TSelectOption,
} from '~/types';

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

export type TUseDevice = (
  /**
   * Device's ID, e.g. the device.name field.
   */
  deviceId: string,
) => TDevice;

export interface TSelections {
  queryLocation: TSelectOption[] | [];
  queryType: TSelectOption | null;
  queryVrf: TSelectOption | null;
}

export interface TMethodsExtension {
  getResponse(d: string): TQueryResponse | null;
  resolvedClose(): void;
  resolvedOpen(): void;
  formReady(): boolean;
  resetForm(): void;
  stateExporter<O extends unknown>(o: O): O | null;
}

export type TLGState = {
  queryVrf: string;
  families: Families;
  queryTarget: string;
  btnLoading: boolean;
  isSubmitting: boolean;
  displayTarget: string;
  queryType: TQueryTypes;
  queryLocation: string[];
  availVrfs: TDeviceVrf[];
  resolvedIsOpen: boolean;
  selections: TSelections;
  responses: { [d: string]: TQueryResponse };
};

export type TLGStateHandlers = {
  exportState<S extends unknown | null>(s: S): S | null;
  getResponse(d: string): TQueryResponse | null;
  resolvedClose(): void;
  resolvedOpen(): void;
  formReady(): boolean;
  resetForm(): void;
  stateExporter<O extends unknown>(o: O): O | null;
};

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
  rpki_state: (v: number, n: TRPKIStates) => string;
};

export type GAEffect = (ga: typeof ReactGA) => void;

export interface GAReturn {
  ga: typeof ReactGA;
  initialize(trackingId: string | null, debug: boolean): void;
  trackPage(path: string): void;
  trackModal(path: string): void;
  trackEvent(event: ReactGA.EventArgs): void;
}
