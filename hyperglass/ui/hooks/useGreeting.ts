import { createState, useState } from '@hookstate/core';
import { Persistence } from '@hookstate/persistence';

import type { TUseGreetingReturn } from './types';

const greeting = createState<boolean>(false);

export function useGreeting(): TUseGreetingReturn {
  const state = useState<boolean>(greeting);
  if (typeof window !== 'undefined') {
    state.attach(Persistence('hyperglass-greeting'));
  }

  function setAck(v: boolean = true): void {
    if (!state.get()) {
      state.set(v);
    }
  }

  return [state.value, setAck];
}
