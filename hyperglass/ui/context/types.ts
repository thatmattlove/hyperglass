import type { IConfig, TFormData } from '~/types';

export interface THyperglassProvider {
  config: IConfig;
  children: React.ReactNode;
}

export interface TGlobalState {
  isSubmitting: boolean;
  formData: TFormData;
}
