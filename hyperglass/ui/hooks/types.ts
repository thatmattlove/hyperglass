import type { State } from '@hookstate/core';
import type * as ReactGA from 'react-ga';
import type { Device, Families, TFormQuery, TSelectOption, Directive } from '~/types';

export type LGQueryKey = [string, TFormQuery];
export type DNSQueryKey = [string, { target: string | null; family: 4 | 6 }];

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

export type TUseDevice = (
  /**
   * Device's ID, e.g. the device.name field.
   */
  deviceId: string,
) => Device;

export interface TSelections {
  queryLocation: TSelectOption[] | [];
  queryType: TSelectOption | null;
  queryGroup: TSelectOption | null;
}

export interface TMethodsExtension {
  getResponse(d: string): QueryResponse | null;
  resolvedClose(): void;
  resolvedOpen(): void;
  formReady(): boolean;
  resetForm(): void;
  stateExporter<O extends unknown>(o: O): O | null;
  getDirective(n: string): Nullable<State<Directive>>;
}

export type TLGState = {
  queryGroup: string;
  families: Families;
  queryTarget: string;
  btnLoading: boolean;
  isSubmitting: boolean;
  displayTarget: string;
  directive: Directive | null;
  queryType: string;
  queryLocation: string[];
  availableGroups: string[];
  availableTypes: Directive[];
  resolvedIsOpen: boolean;
  selections: TSelections;
  responses: { [d: string]: QueryResponse };
};

export type TLGStateHandlers = {
  exportState<S extends unknown | null>(s: S): S | null;
  getResponse(d: string): QueryResponse | null;
  resolvedClose(): void;
  resolvedOpen(): void;
  formReady(): boolean;
  resetForm(): void;
  stateExporter<O extends unknown>(o: O): O | null;
  getDirective(n: string): Nullable<State<Directive>>;
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
