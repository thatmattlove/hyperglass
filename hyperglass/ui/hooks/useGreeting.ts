import { createState, useState } from '@hookstate/core';
import { Persistence } from '@hookstate/persistence';
import { useConfig } from '~/context';

import type { TUseGreetingReturn } from './types';

const ackState = createState<boolean>(false);
const openState = createState<boolean>(false);

/**
 * Hook to manage the greeting, a.k.a. the popup at config path web.greeting.
 */
export function useGreeting(): TUseGreetingReturn {
  const ack = useState<boolean>(ackState);
  const isOpen = useState<boolean>(openState);
  const { web } = useConfig();

  if (typeof window !== 'undefined') {
    ack.attach(Persistence('hyperglass-greeting'));
  }

  function open() {
    return isOpen.set(true);
  }
  function close() {
    return isOpen.set(false);
  }

  function greetingReady(): boolean {
    if (ack.get()) {
      // If the acknowledgement is already set, no further evaluation is needed.
      return true;
    } else if (!web.greeting.required && !ack.get()) {
      // If the acknowledgement is not set, but is also not required, then pass.
      return true;
    } else if (web.greeting.required && !ack.get()) {
      // If the acknowledgement is not set, but is required, then fail.
      return false;
    } else {
      return false;
    }
  }

  return { ack, isOpen, greetingReady, open, close };
}
