import type { ReactNode, RefObject } from 'react';
import type { IConfig, IFormData } from '~/types';

export interface IHyperglassProvider {
  config: IConfig;
  children: ReactNode;
}

export interface IGlobalState {
  isSubmitting: boolean;
  formData: IFormData;
}
