import { useMemo } from 'react';
import { useFormState } from './use-form-state';

import type { Directive } from '~/types';

export function useDirective(): Nullable<Directive> {
  const { getDirective, form } = useFormState(({ getDirective, form }) => ({ getDirective, form }));

  return useMemo<Nullable<Directive>>(() => {
    if (form.queryType === '') {
      return null;
    }
    const directive = getDirective();
    return directive;

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.queryType, getDirective]);
}
