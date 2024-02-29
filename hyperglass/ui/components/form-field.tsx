import { Flex, FormControl, FormErrorMessage, FormLabel } from '@chakra-ui/react';
import { useMemo } from 'react';
import { useFormContext } from 'react-hook-form';
import { If, Then } from 'react-if';
import { useBooleanValue, useColorValue } from '~/hooks';

import type { FormControlProps } from '@chakra-ui/react';
import type { FieldError } from 'react-hook-form';
import type { FormData } from '~/types';

interface FormFieldProps extends FormControlProps {
  name: string;
  label: string;
  hiddenLabels?: boolean;
  labelAddOn?: React.ReactNode;
  fieldAddOn?: React.ReactNode;
}

export const FormField = (props: FormFieldProps): JSX.Element => {
  const { name, label, children, labelAddOn, fieldAddOn, hiddenLabels = false, ...rest } = props;
  const labelColor = useColorValue('blackAlpha.700', 'whiteAlpha.700');
  const errorColor = useColorValue('red.500', 'red.300');
  const opacity = useBooleanValue(hiddenLabels, 0, undefined);

  const { formState } = useFormContext<FormData>();

  const error = useMemo<FieldError | null>(() => {
    if (name in formState.errors) {
      console.group(`Error on field '${label}'`);
      console.warn(formState.errors[name as keyof FormData]);
      console.groupEnd();
      return formState.errors[name as keyof FormData] as FieldError;
    }
    return null;
  }, [formState, label, name]);

  return (
    <FormControl
      mx={2}
      w="100%"
      maxW="100%"
      flexDir="column"
      alignItems="center"
      my={{ base: 2, lg: 4 }}
      isInvalid={error !== null}
      {...rest}
    >
      <FormLabel
        pr={0}
        mb={{ lg: 4 }}
        htmlFor={name}
        display="flex"
        opacity={opacity}
        fontWeight="bold"
        alignItems="center"
        justifyContent="space-between"
        color={error !== null ? errorColor : labelColor}
      >
        {label}
        <If condition={typeof labelAddOn !== 'undefined'}>
          <Then>{labelAddOn}</Then>
        </If>
      </FormLabel>
      {children}
      <If condition={typeof fieldAddOn !== 'undefined'}>
        <Then>
          <Flex justify="flex-end" pt={3}>
            {fieldAddOn}
          </Flex>
        </Then>
      </If>
      <FormErrorMessage opacity={opacity}>{error?.message}</FormErrorMessage>
    </FormControl>
  );
};
