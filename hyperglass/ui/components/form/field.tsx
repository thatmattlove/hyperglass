import { useState, useEffect } from 'react';
import { Flex, FormControl, FormLabel, FormErrorMessage } from '@chakra-ui/react';
import { useFormContext } from 'react-hook-form';
import { If } from '~/components';
import { useColorValue } from '~/context';
import { useBooleanValue } from '~/hooks';

import type { FieldError } from 'react-hook-form';
import type { TField } from './types';

export const FormField: React.FC<TField> = (props: TField) => {
  const { name, label, children, labelAddOn, fieldAddOn, hiddenLabels = false, ...rest } = props;
  const labelColor = useColorValue('blackAlpha.700', 'whiteAlpha.700');
  const errorColor = useColorValue('red.500', 'red.300');
  const opacity = useBooleanValue(hiddenLabels, 0, undefined);

  const [error, setError] = useState<Nullable<FieldError>>(null);

  const {
    formState: { errors },
  } = useFormContext();

  useEffect(() => {
    if (name in errors) {
      console.dir(errors);
      setError(errors[name]);
      console.warn(`Error on field '${label}': ${error?.message}`);
    }
  }, [error, errors, setError]);

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
        pl={1}
        pr={0}
        htmlFor={name}
        display="flex"
        opacity={opacity}
        alignItems="center"
        justifyContent="space-between"
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
