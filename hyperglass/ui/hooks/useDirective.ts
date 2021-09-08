import { useMemo } from 'react';
import { useLGMethods, useLGState } from './useLGState';

import type { TDirective } from '~/types';

export function useDirective(): Nullable<TDirective> {
  const { queryType, queryGroup } = useLGState();
  const { getDirective } = useLGMethods();

  return useMemo((): Nullable<TDirective> => {
    if (queryType.value === '') {
      return null;
    }
    const directive = getDirective(queryType.value);
    if (directive !== null) {
      return directive.value;
    }
    return null;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [queryType.value, queryGroup.value, getDirective]);
}
