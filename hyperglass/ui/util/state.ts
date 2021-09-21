import { devtools } from 'zustand/middleware';

import type { StateCreator } from 'zustand';

/**
 * Wrap a zustand state function with devtools, if applicable.
 *
 * @param store zustand store function.
 * @param name Store name.
 */
// eslint-disable-next-line @typescript-eslint/ban-types
export function withDev<T extends object = {}>(
  store: StateCreator<T>,
  name: string,
): StateCreator<T> {
  if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
    return devtools<T>(store, { name });
  }
  return store;
}
