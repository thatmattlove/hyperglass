import create from 'zustand';
import { persist } from 'zustand/middleware';
import { withDev } from '~/util';

interface UseGreeting {
  isAck: boolean;
  isOpen: boolean;
  greetingReady: boolean;
  ack(value: boolean, required: boolean): void;
  open(): void;
  close(): void;
}

export const useGreeting = create<UseGreeting>(
  persist(
    withDev<UseGreeting>(
      set => ({
        isOpen: false,
        isAck: false,
        greetingReady: false,
        ack(isAck: boolean, required: boolean): void {
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
