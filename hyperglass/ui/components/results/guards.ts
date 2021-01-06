/* eslint @typescript-eslint/no-explicit-any: 0 */
/* eslint @typescript-eslint/explicit-module-boundary-types: 0 */

export function isStackError(error: any): error is Error {
  return typeof error !== 'undefined' && error !== null && 'message' in error;
}

export function isFetchError(error: any): error is Response {
  return typeof error !== 'undefined' && error !== null && 'statusText' in error;
}

export function isLGError(error: any): error is TQueryResponse {
  return typeof error !== 'undefined' && error !== null && 'output' in error;
}

/**
 * Returns true if the response is an LG error, false if not.
 */
export function isLGOutputOrError(data: any): data is TQueryResponse {
  return typeof data !== 'undefined' && data !== null && data?.level !== 'success';
}
