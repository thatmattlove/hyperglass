import { useState } from '@hookstate/core';
import { Persistence } from '@hookstate/persistence';

import type { TUseGreetingReturn } from './types';

export function useGreeting(): TUseGreetingReturn {
  const state = useState<boolean>(false);
  state.attach(Persistence('plugin-persisted-data-key'));

  function setAck(): void {
    if (!state.get()) {
      state.set(true);
    }
    return;
  }

  return [state.value, setAck];
}
