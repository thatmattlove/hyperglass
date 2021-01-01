export function isStackError(error: any): error is Error {
  return error !== null && 'message' in error;
}

export function isFetchError(error: any): error is Response {
  return error !== null && 'statusText' in error;
}

export function isLGError(error: any): error is TQueryResponse {
  return typeof error !== 'undefined' && error !== null && 'output' in error;
}
