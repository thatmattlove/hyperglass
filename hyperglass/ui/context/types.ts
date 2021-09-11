import type { State } from '@hookstate/core';
import type { Config, FormData } from '~/types';

export interface THyperglassProvider {
  config: Config;
  children: React.ReactNode;
}

export interface TGlobalState {
  isSubmitting: boolean;
  formData: FormData;
}

export interface TUseGlobalState {
  isSubmitting: State<TGlobalState['isSubmitting']>;
  formData: State<TGlobalState['formData']>;
  resetForm(): void;
}
