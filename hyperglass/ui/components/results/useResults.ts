import { useEffect } from 'react';
import { createState, useState } from '@hookstate/core';

import type { Plugin, State, PluginStateControl } from '@hookstate/core';
import type { TUseResults, TUseResultsMethods, UseResultsReturn } from './types';

const MethodsId = Symbol('UseResultsMethods');

/**
 * Plugin methods.
 */
class MethodsInstance {
  /**
   * Toggle a location's open/closed state.
   */
  public toggle(state: State<TUseResults>, loc: string) {
    state.locations[loc].open.set(p => !p);
  }
  /**
   * Set a location's completion state.
   */
  public setComplete(state: State<TUseResults>, loc: string) {
    state.locations[loc].merge({ complete: true });
    const thisLoc = state.locations[loc];
    if (
      state.firstOpen.value === null &&
      state.locations.keys.includes(loc) &&
      state.firstOpen.value !== thisLoc.index.value
    ) {
      state.firstOpen.set(thisLoc.index.value);
      this.toggle(state, loc);
    }
  }
  /**
   * Get the currently open panels. Passed to Chakra UI's index prop for internal state management.
   */
  public getOpen(state: State<TUseResults>) {
    const open = state.locations.keys
      .filter(k => state.locations[k].complete.value && state.locations[k].open.value)
      .map(k => state.locations[k].index.value);
    return open;
  }
}

/**
 * hookstate plugin to provide convenience functions & tracking for the useResults hook.
 */
function Methods(inst?: State<TUseResults>): Plugin | TUseResultsMethods {
  if (inst) {
    const [instance] = inst.attach(MethodsId) as [
      MethodsInstance | Error,
      PluginStateControl<TUseResults>,
    ];

    if (instance instanceof Error) {
      throw instance;
    }

    return {
      toggle: (loc: string) => instance.toggle(inst, loc),
      setComplete: (loc: string) => instance.setComplete(inst, loc),
      getOpen: () => instance.getOpen(inst),
    } as TUseResultsMethods;
  }
  return {
    id: MethodsId,
    init: () => {
      /* eslint @typescript-eslint/ban-types: 0 */
      return new MethodsInstance() as {};
    },
  } as Plugin;
}
const initialState = { firstOpen: null, locations: {} } as TUseResults;
const resultsState = createState<TUseResults>(initialState);

/**
 * Track the state of each result, and whether or not each panel is open.
 */
export function useResults(initial: TUseResults['locations']): UseResultsReturn {
  // Initialize the global state before instantiating the hook, only once.
  useEffect(() => {
    if (resultsState.firstOpen.value === null && resultsState.locations.keys.length === 0) {
      resultsState.set({ firstOpen: null, locations: initial });
    }
  }, []);

  const results = useState(resultsState);
  results.attach(Methods as () => Plugin);

  const methods = Methods(results) as TUseResultsMethods;

  // Reset the state on unmount.
  useEffect(() => {
    return () => {
      results.set(initialState);
    };
  }, []);

  return { results, ...methods };
}
