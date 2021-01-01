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

interface TGlobalStateFunctions {
  resetForm(): void;
}

// export type TUseGlobalState = State<TGlobalState> & TGlobalStateFunctions;

export interface TUseGlobalState {
  isSubmitting: State<TGlobalState['isSubmitting']>;
  formData: State<TGlobalState['formData']>;
  resetForm(): void;
}
