import type { State } from '@hookstate/core';
import type { IConfig, TFormData } from '~/types';

export interface THyperglassProvider {
  config: IConfig;
  children: React.ReactNode;
}

export interface TGlobalState {
  isSubmitting: boolean;
  formData: TFormData;
}

export interface TUseGlobalState {
  isSubmitting: State<TGlobalState['isSubmitting']>;
  formData: State<TGlobalState['formData']>;
  resetForm(): void;
}
