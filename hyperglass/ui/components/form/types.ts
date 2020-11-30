import type { FormControlProps } from '@chakra-ui/react';
import type { FieldError } from 'react-hook-form';

export interface TField extends FormControlProps {
  name: string;
  label: string;
  error?: FieldError;
  hiddenLabels: boolean;
  labelAddOn?: React.ReactNode;
  fieldAddOn?: React.ReactNode;
}
