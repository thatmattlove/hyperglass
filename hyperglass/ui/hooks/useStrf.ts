import { useCallback } from 'react';
import format from 'string-format';

import type { UseStrfArgs } from './types';

/**
 * Format a string with variables, like Python's string.format()
 */
export function useStrf(): (str: string, fmt: UseStrfArgs, fallback?: string) => string {
  return useCallback(
    (str: string, fmt: UseStrfArgs, fallback?: string) => format(str, fmt) ?? fallback,
    [],
  );
}
