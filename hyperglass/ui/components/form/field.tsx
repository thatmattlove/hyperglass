import { useMemo } from 'react';
import { Flex, FormControl, FormLabel, FormErrorMessage } from '@chakra-ui/react';
import { useFormContext } from 'react-hook-form';
import { If } from '~/components';
import { useColorValue } from '~/context';
import { useBooleanValue } from '~/hooks';

import type { FieldError } from 'react-hook-form';
import type { FormData } from '~/types';
import type { TField } from './types';

export const FormField = (props: TField): JSX.Element => {
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
      isInvalid={error !== null}
      my={{ base: 2, lg: 4 }}
      {...rest}
    >
      <FormLabel
        pr={0}
        mb={{ lg: 4 }}
        htmlFor={name}
        display="flex"
        opacity={opacity}
        alignItems="center"
        justifyContent="space-between"
        fontWeight="bold"
        color={error !== null ? errorColor : labelColor}
      >
        {label}
        <If c={typeof labelAddOn !== 'undefined'}>{labelAddOn}</If>
      </FormLabel>
      {children}
      <If c={typeof fieldAddOn !== 'undefined'}>
        <Flex justify="flex-end" pt={3}>
          {fieldAddOn}
        </Flex>
      </If>
      <FormErrorMessage opacity={opacity}>{error?.message}</FormErrorMessage>
    </FormControl>
  );
};
