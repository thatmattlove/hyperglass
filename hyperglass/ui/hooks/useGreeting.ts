import { useState } from '@hookstate/core';
import { Persistence } from '@hookstate/persistence';

import type { TUseGreetingReturn } from './types';

export function useGreeting(): TUseGreetingReturn {
  const state = useState<boolean>(false);
  if (typeof window !== 'undefined') {
    state.attach(Persistence('hyperglass-greeting'));
  }

  function setAck(v: boolean = true): void {
    if (!state.get()) {
      state.set(v);
    }
    return;
  }

  return [state.value, setAck];
}
