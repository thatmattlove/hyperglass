import { useState, createState } from '@hookstate/core';

import type { State } from '@hookstate/core';
import type { Families, TDeviceVrf, TQueryTypes, TFormData } from '~/types';

type TLGState = {
  isSubmitting: boolean;
  queryVrf: string;
  families: Families;
  queryTarget: string;
  btnLoading: boolean;
  displayTarget: string;
  queryType: TQueryTypes;
  queryLocation: string[];
  availVrfs: TDeviceVrf[];
  resolvedIsOpen: boolean;
  fqdnTarget: string | null;
  formData: TFormData;
};

type TLGStateHandlers = {
  resolvedOpen(): void;
  resolvedClose(): void;
  resetForm(): void;
};

const LGState = createState<TLGState>({
  isSubmitting: false,
  resolvedIsOpen: false,
  displayTarget: '',
  queryLocation: [],
  btnLoading: false,
  fqdnTarget: null,
  queryTarget: '',
  queryType: '',
  availVrfs: [],
  queryVrf: '',
  families: [],
  formData: { query_location: [], query_target: '', query_type: '', query_vrf: '' },
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
    });
  }

  return { resetForm, resolvedOpen, resolvedClose, ...state };
}
