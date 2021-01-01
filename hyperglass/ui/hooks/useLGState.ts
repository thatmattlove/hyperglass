import { useCallback } from 'react';
import { useState, createState } from '@hookstate/core';
import isEqual from 'react-fast-compare';
import { all } from '~/util';

import type { State, PluginStateControl, Plugin } from '@hookstate/core';
import type { Families, TDeviceVrf, TQueryTypes, TSelectOption } from '~/types';

const PluginID = Symbol('Methods');

/**
 * Public API
 */
interface MethodsExtension {
  getResponse(d: string): TQueryResponse | null;
  resolvedClose(): void;
  resolvedOpen(): void;
  formReady(): boolean;
  resetForm(): void;
}

class MethodsInstance {
  public resolvedOpen(state: State<TLGState>) {
    state.resolvedIsOpen.set(true);
  }
  public resolvedClose(state: State<TLGState>) {
    state.resolvedIsOpen.set(false);
  }
  public getResponse(state: State<TLGState>, device: string): TQueryResponse | null {
    if (device in state.responses) {
      return state.responses[device].value;
    } else {
      return null;
    }
  }
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
}

function Methods(): Plugin;
function Methods(inst: State<TLGState>): MethodsExtension;
function Methods(inst?: State<TLGState>): Plugin | MethodsExtension {
  if (inst) {
    const [instance] = inst.attach(PluginID) as [
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
    };
  }
  return {
    id: PluginID,
    init: () => {
      return new MethodsInstance() as {};
    },
  };
}

interface TSelections {
  queryLocation: TSelectOption[] | [];
  queryType: TSelectOption | null;
  queryVrf: TSelectOption | null;
}

type TLGState = {
  queryVrf: string;
  families: Families;
  queryTarget: string;
  btnLoading: boolean;
  isSubmitting: boolean;
  displayTarget: string;
  queryType: TQueryTypes;
  queryLocation: string[];
  availVrfs: TDeviceVrf[];
  resolvedIsOpen: boolean;
  selections: TSelections;
  responses: { [d: string]: TQueryResponse };
};

type TLGStateHandlers = {
  exportState<S extends unknown | null>(s: S): S | null;
  getResponse(d: string): TQueryResponse | null;
  resolvedClose(): void;
  resolvedOpen(): void;
  formReady(): boolean;
  resetForm(): void;
};

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

export function useLGState(): State<TLGState> {
  return useState<TLGState>(LGState);
}

function stateExporter<O extends unknown>(obj: O): O | null {
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

export function useLGMethods(): TLGStateHandlers {
  const state = useLGState();
  state.attach(Methods);
  const exporter = useCallback(stateExporter, [isEqual]);
  return {
    exportState(s) {
      return exporter(s);
    },
    ...Methods(state),
  };
}
