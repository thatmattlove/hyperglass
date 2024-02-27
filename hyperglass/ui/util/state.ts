import { devtools } from 'zustand/middleware';

import type { StateCreator, SetState, GetState, StoreApi } from 'zustand';

/**
 * Wrap a zustand state function with devtools, if applicable.
 *
 * @param store zustand store function.
 * @param name Store name.
 */
export function withDev<T extends object = {}>(
  store: StateCreator<T>,
  name: string,
): StateCreator<T> {
  if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
    return devtools<T, SetState<T>, GetState<T>, StoreApi<T>>(store, { name });
  }
  return store;
}
