import { useCallback } from 'react';
import format from 'string-format';

type UseStrfArgs = { [k: string]: unknown } | string;

/**
 * Format a string with variables, like Python's string.format()
 */
export function useStrf(): (str: string, fmt: UseStrfArgs, fallback?: string) => string {
  return useCallback(
    (str: string, fmt: UseStrfArgs, fallback?: string) => format(str, fmt) ?? fallback,
    [],
  );
}
