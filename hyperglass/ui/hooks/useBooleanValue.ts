import { useMemo } from 'react';

/**
 * Track the state of a boolean and return values based on its state.
 */
export function useBooleanValue<T extends unknown, F extends unknown>(
  status: boolean,
  ifTrue: T,
  ifFalse: F,
): T | F {
  return useMemo(() => {
    if (status) {
      return ifTrue;
    } else {
      return ifFalse;
    }
  }, [status]);
}
