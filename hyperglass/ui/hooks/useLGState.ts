import { useCallback } from 'react';
import { useState, createState } from '@hookstate/core';
import isEqual from 'react-fast-compare';
import { all } from '~/util';

import type { State, PluginStateControl, Plugin } from '@hookstate/core';
import type { TLGState, TLGStateHandlers, TMethodsExtension } from './types';

const MethodsId = Symbol('Methods');

/**
 * hookstate plugin to provide convenience functions for the useLGState hook.
 */
class MethodsInstance {
  /**
   * Set the DNS resolver Popover to opened.
   */
  public resolvedOpen(state: State<TLGState>) {
    state.resolvedIsOpen.set(true);
  }
  /**
   * Set the DNS resolver Popover to closed.
   */
  public resolvedClose(state: State<TLGState>) {
    state.resolvedIsOpen.set(false);
  }
  /**
   * Find a response based on the device ID.
   */
  public getResponse(state: State<TLGState>, device: string): TQueryResponse | null {
    if (device in state.responses) {
      return state.responses[device].value;
    } else {
      return null;
    }
  }
  /**
   * Determine if the form is ready for submission, e.g. all fields have values and isSubmitting
   * has been set to true. This ultimately controls the UI layout.
   */
  public formReady(state: State<TLGState>): boolean {
    return (
      state.isSubmitting.value &&
      all(
        ...[
          state.queryVrf.value !== '',
          state.queryType.value !== '',
          state.queryTarget.value !== '',
          state.queryLocation.length !== 0,
        ],
      )
    );
  }
  /**
   * Reset form values affected by the form state to their default values.
   */
  public resetForm(state: State<TLGState>) {
    state.merge({
      queryVrf: '',
      families: [],
      queryType: '',
      responses: {},
      queryTarget: '',
      queryLocation: [],
      displayTarget: '',
      btnLoading: false,
      isSubmitting: false,
      resolvedIsOpen: false,
      availVrfs: [],
      selections: { queryLocation: [], queryType: null, queryVrf: null },
    });
  }
  public stateExporter<O extends unknown>(obj: O): O | null {
    let result = null;
    if (obj === null) {
      return result;
    }
    try {
      result = JSON.parse(JSON.stringify(obj));
    } catch (err) {
      console.error(err.message);
    }
    return result;
  }
}

/**
 * Plugin Initialization.
 */
function Methods(): Plugin;
/**
 * Plugin Attachment.
 */
function Methods(inst: State<TLGState>): TMethodsExtension;
/**
 * Plugin Instance.
 */
function Methods(inst?: State<TLGState>): Plugin | TMethodsExtension {
  if (inst) {
    const [instance] = inst.attach(MethodsId) as [
      MethodsInstance | Error,
      PluginStateControl<TLGState>,
    ];

    if (instance instanceof Error) {
      throw instance;
    }

    return {
      resetForm: () => instance.resetForm(inst),
      formReady: () => instance.formReady(inst),
      resolvedOpen: () => instance.resolvedOpen(inst),
      resolvedClose: () => instance.resolvedClose(inst),
      getResponse: device => instance.getResponse(inst, device),
      stateExporter: obj => instance.stateExporter(obj),
    };
  }
  return {
    id: MethodsId,
    init: () => {
      /* eslint @typescript-eslint/ban-types: 0 */
      return new MethodsInstance() as {};
    },
  };
}

const LGState = createState<TLGState>({
  selections: { queryLocation: [], queryType: null, queryVrf: null },
  resolvedIsOpen: false,
  isSubmitting: false,
  displayTarget: '',
  queryLocation: [],
  btnLoading: false,
  queryTarget: '',
  queryType: '',
  availVrfs: [],
  responses: {},
  queryVrf: '',
  families: [],
});

/**
 * Global state hook for state used throughout hyperglass.
 */
export function useLGState(): State<TLGState> {
  return useState<TLGState>(LGState);
}

/**
 * Plugin for useLGState() that provides convenience methods for its state.
 */
export function useLGMethods(): TLGStateHandlers {
  const state = useLGState();
  state.attach(Methods);
  const exporter = useCallback(Methods(state).stateExporter, [isEqual]);
  return {
    exportState(s) {
      return exporter(s);
    },
    ...Methods(state),
  };
}
