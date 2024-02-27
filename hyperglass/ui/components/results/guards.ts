// biome-ignore lint/suspicious/noExplicitAny: type guard
export function isStackError(error: any): error is Error {
  return typeof error !== 'undefined' && error !== null && 'message' in error;
}

// biome-ignore lint/suspicious/noExplicitAny: type guard
export function isFetchError(error: any): error is Response {
  return typeof error !== 'undefined' && error !== null && 'statusText' in error;
}

// biome-ignore lint/suspicious/noExplicitAny: type guard
export function isLGError(error: any): error is QueryResponse {
  return typeof error !== 'undefined' && error !== null && 'output' in error;
}

/**
 * Returns true if the response is an LG error, false if not.
 */
// biome-ignore lint/suspicious/noExplicitAny: type guard
export function isLGOutputOrError(data: any): data is QueryResponse {
  return typeof data !== 'undefined' && data !== null && data?.level !== 'success';
}
