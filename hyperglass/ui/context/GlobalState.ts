import { createState, useState } from '@hookstate/core';
import type { TGlobalState, TUseGlobalState } from './types';

const defaultFormData = {
  query_location: [],
  query_target: '',
  query_type: '',
  query_vrf: '',
} as TGlobalState['formData'];

const globalState = createState<TGlobalState>({
  isSubmitting: false,
  formData: defaultFormData,
});

export function useGlobalState(): TUseGlobalState {
  const state = useState<TGlobalState>(globalState);
  function resetForm(): void {
    state.formData.set(defaultFormData);
    state.isSubmitting.set(false);
  }
  return { resetForm, ...state };
}
