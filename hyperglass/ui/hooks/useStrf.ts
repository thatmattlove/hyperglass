import { useMemo } from 'react';
import format from 'string-format';

import type { UseStrfArgs } from './types';

/**
 * Format a string with variables, like Python's string.format()
 */
export function useStrf(str: string, fmt: UseStrfArgs, ...deps: unknown[]): string {
  return useMemo(() => format(str, fmt), deps);
}
