import type { TValidQueryTypes, TStringTableData, TQueryResponseString } from './data';
import type { TQueryContent } from './config';

export function isQueryType(q: any): q is TValidQueryTypes {
  let result = false;
  if (
    typeof q === 'string' &&
    ['bgp_route', 'bgp_community', 'bgp_aspath', 'ping', 'traceroute'].includes(q)
  ) {
    result = true;
  }
  return result;
}

export function isString(a: any): a is string {
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
