/* eslint @typescript-eslint/explicit-module-boundary-types: off */
/* eslint @typescript-eslint/no-explicit-any: off */
import type { State } from '@hookstate/core';
import type { TValidQueryTypes, TStringTableData, TQueryResponseString } from './data';
import type { TSelectOption } from './common';
import type { TQueryContent } from './config';

export function isQueryType(q: unknown): q is TValidQueryTypes {
  let result = false;
  if (
    typeof q === 'string' &&
    ['bgp_route', 'bgp_community', 'bgp_aspath', 'ping', 'traceroute'].includes(q)
  ) {
    result = true;
  }
  return result;
}

export function isString(a: unknown): a is string {
  return typeof a === 'string';
}

export function isStructuredOutput(data: any): data is TStringTableData {
  return typeof data !== 'undefined' && 'output' in data && typeof data.output !== 'string';
}

export function isStringOutput(data: any): data is TQueryResponseString {
  return typeof data !== 'undefined' && 'output' in data && typeof data.output === 'string';
}

export function isQueryContent(c: any): c is TQueryContent {
  return typeof c !== 'undefined' && c !== null && 'content' in c;
}

/**
 * Determine if an object is a Select option.
 */
export function isSelectOption(a: any): a is NonNullable<TSelectOption> {
  return typeof a !== 'undefined' && a !== null && 'label' in a && 'value' in a;
}

/**
 * Determine if an object is a HookState Proxy.
 */
export function isState<S>(a: any): a is State<NonNullable<S>> {
  let result = false;
  if (typeof a !== 'undefined' && a !== null) {
    if (
      'get' in a &&
      typeof a.get === 'function' &&
      'set' in a &&
      typeof a.set === 'function' &&
      'promised' in a
    ) {
      result = true;
    }
  }
  return result;
}
