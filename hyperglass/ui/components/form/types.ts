import type { FormControlProps } from '@chakra-ui/react';
import type { Control } from 'react-hook-form';
import type { TDeviceVrf, TBGPCommunity, OnChangeArgs } from '~/types';
import type { ValidationError } from 'yup';

export type TFormError = Pick<ValidationError, 'message' | 'type'>;

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

export interface TQueryVrf extends TQuerySelectField {
  vrfs: TDeviceVrf[];
}

export interface TCommunitySelect {
  name: string;
  onChange: OnChange;
  communities: TBGPCommunity[];
  register: Control['register'];
}

export interface TQueryTarget {
  name: string;
  placeholder: string;
  register: Control['register'];
  onChange(e: OnChangeArgs): void;
}

export interface TResolvedTarget {
  setTarget(e: OnChangeArgs): void;
  errorClose(): void;
}
