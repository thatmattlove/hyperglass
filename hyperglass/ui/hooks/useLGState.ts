import { useState, createState } from '@hookstate/core';

import type { State } from '@hookstate/core';
import type { Families, TDeviceVrf, TQueryTypes, TFormData } from '~/types';

type TLGState = {
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
};

const LGState = createState<TLGState>({
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

  return { resolvedOpen, resolvedClose, ...state };
}
