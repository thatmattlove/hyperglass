import type { FormControlProps } from '@chakra-ui/react';
import type { UseFormRegister } from 'react-hook-form';
import type { OnChangeArgs, FormData } from '~/types';

export interface TField extends FormControlProps {
  name: string;
  label: string;
  hiddenLabels?: boolean;
  labelAddOn?: React.ReactNode;
  fieldAddOn?: React.ReactNode;
}

export type OnChange = (f: OnChangeArgs) => void;

export interface TQuerySelectField {
  onChange: OnChange;
  label: string;
}

export interface TQueryGroup extends TQuerySelectField {
  groups: string[];
}

export interface TQueryTarget {
  name: string;
  placeholder: string;
  register: UseFormRegister<FormData>;
  onChange(e: OnChangeArgs): void;
}

export interface TResolvedTarget {
  setTarget(e: OnChangeArgs): void;
  errorClose(): void;
}
