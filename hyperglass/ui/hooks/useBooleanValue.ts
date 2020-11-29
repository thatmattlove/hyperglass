import { useMemo } from 'react';

export function useBooleanValue<T extends any, F extends any>(
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
