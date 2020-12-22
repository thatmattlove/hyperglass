import { useState, createState } from '@hookstate/core';

import type { State } from '@hookstate/core';
import type { Families, TDeviceVrf, TQueryTypes, TFormData } from '~/types';

type TLGState = {
  queryVrf: string;
  families: Families;
  queryTarget: string;
  btnLoading: boolean;
  formData: TFormData;
  isSubmitting: boolean;
  displayTarget: string;
  queryType: TQueryTypes;
  queryLocation: string[];
  availVrfs: TDeviceVrf[];
  resolvedIsOpen: boolean;
  fqdnTarget: string | null;
  responses: { [d: string]: TQueryResponse };
};

type TLGStateHandlers = {
  resolvedOpen(): void;
  resolvedClose(): void;
  resetForm(): void;
  getResponse(d: string): TQueryResponse | null;
};

const LGState = createState<TLGState>({
  formData: { query_location: [], query_target: '', query_type: '', query_vrf: '' },
  resolvedIsOpen: false,
  isSubmitting: false,
  displayTarget: '',
  queryLocation: [],
  btnLoading: false,
  fqdnTarget: null,
  queryTarget: '',
  queryType: '',
  availVrfs: [],
  responses: {},
  queryVrf: '',
  families: [],
});

export function useLGState(): State<TLGState> & TLGStateHandlers {
  const state = useState<TLGState>(LGState);
  function resolvedOpen() {
    state.resolvedIsOpen.set(true);
  }
  function resolvedClose() {
    state.resolvedIsOpen.set(false);
  }
  function resetForm() {
    state.merge({
      queryVrf: '',
      families: [],
      queryType: '',
      queryTarget: '',
      fqdnTarget: null,
      queryLocation: [],
      displayTarget: '',
      resolvedIsOpen: false,
      btnLoading: false,
      formData: { query_location: [], query_target: '', query_type: '', query_vrf: '' },
      responses: {},
    });
  }
  function getResponse(device: string): TQueryResponse | null {
    if (device in state.responses) {
      return state.responses[device].value;
    } else {
      return null;
    }
  }

  return { resetForm, resolvedOpen, resolvedClose, getResponse, ...state };
}
