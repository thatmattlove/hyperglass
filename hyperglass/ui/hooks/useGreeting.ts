import create from 'zustand';
import { persist } from 'zustand/middleware';
import { useConfig } from '~/context';
import { withDev } from '~/util';

import type { StateSelector, EqualityChecker } from 'zustand';
import type { UseGreeting } from './types';

export function useGreeting(): UseGreeting;
export function useGreeting<U extends ValueOf<UseGreeting>>(
  selector: StateSelector<UseGreeting, U>,
  equalityFn?: EqualityChecker<U>,
): U;
export function useGreeting<U extends Partial<UseGreeting>>(
  selector: StateSelector<UseGreeting, U>,
  equalityFn?: EqualityChecker<U>,
): U;
export function useGreeting<U extends UseGreeting>(
  selector?: StateSelector<UseGreeting, U>,
  equalityFn?: EqualityChecker<U>,
): U {
  const {
    web: {
      greeting: { required },
    },
  } = useConfig();
  const storeFn = create<UseGreeting>(
    persist(
      withDev<UseGreeting>(
        set => ({
          isOpen: false,
          isAck: false,
          greetingReady: false,
          ack(isAck: boolean): void {
            const greetingReady = isAck ? true : !required ? true : false;
            set(() => ({ isAck, greetingReady, isOpen: false }));
          },
          open(): void {
            set(() => ({ isOpen: true }));
          },
          close(): void {
            set(() => ({ isOpen: false }));
          },
        }),
        'useGreeting',
      ),
      { name: 'hyperglass-greeting' },
    ),
  );
  if (typeof selector === 'function') {
    return storeFn<U>(selector, equalityFn);
  }
  return storeFn() as U;
}
