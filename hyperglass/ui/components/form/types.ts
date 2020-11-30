import type { FormControlProps } from '@chakra-ui/react';
import type { FieldError } from 'react-hook-form';
import type { TNetwork } from '~/types';

export interface TField extends FormControlProps {
  name: string;
  label: string;
  error?: FieldError;
  hiddenLabels: boolean;
  labelAddOn?: React.ReactNode;
  fieldAddOn?: React.ReactNode;
}

export type OnChangeArgs = { label: string; value: string | string[] };

export interface TQueryLocation {
  locations: TNetwork[];
  onChange(f: OnChangeArgs | OnChangeArgs[]): void;
  label: string;
}
