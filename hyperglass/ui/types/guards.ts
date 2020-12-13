import { TValidQueryTypes } from './data';

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
