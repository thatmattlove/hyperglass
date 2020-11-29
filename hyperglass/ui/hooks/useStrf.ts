import { useMemo } from 'react';
import format from 'string-format';

type FmtArgs = { [k: string]: any } | string;

export function useStrf(str: string, fmt: FmtArgs, ...deps: any[]): string {
  return useMemo(() => format(str, fmt), deps);
}
