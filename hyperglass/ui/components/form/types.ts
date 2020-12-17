import type { FormControlProps } from '@chakra-ui/react';
import type { FieldError, Control } from 'react-hook-form';
import type { TDeviceVrf, TBGPCommunity, OnChangeArgs, TFormData } from '~/types';

export interface TField extends FormControlProps {
  name: string;
  label: string;
  errors?: FieldError | FieldError[];
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
  unregister: Control['unregister'];
}

/**
 *  placeholder,
    register,
    unregister,
    setFqdn,
    
    name,
    value,
    
    setTarget,
    resolveTarget,

    displayValue,
    setDisplayValue,
 */
export interface TQueryTarget {
  name: string;
  placeholder: string;
  displayValue: string;
  resolveTarget: boolean;
  setFqdn(f: string | null): void;
  setTarget(e: OnChangeArgs): void;
  register: Control['register'];
  value: TFormData['query_target'];
  setDisplayValue(d: string): void;
  unregister: Control['unregister'];
}

export interface TResolvedTarget {
  setTarget(e: OnChangeArgs): void;
}
