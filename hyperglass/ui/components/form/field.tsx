import { Flex, FormControl, FormLabel, FormErrorMessage } from '@chakra-ui/react';
import { useFormContext } from 'react-hook-form';
import { If } from '~/components';
import { useColorValue } from '~/context';
import { useBooleanValue } from '~/hooks';

import { TField, TFormError } from './types';

export const FormField: React.FC<TField> = (props: TField) => {
  const { name, label, children, labelAddOn, fieldAddOn, hiddenLabels = false, ...rest } = props;
  const labelColor = useColorValue('blackAlpha.700', 'whiteAlpha.700');
  const errorColor = useColorValue('red.500', 'red.300');
  const opacity = useBooleanValue(hiddenLabels, 0, undefined);

  const { errors } = useFormContext();

  const error = name in errors && (errors[name] as TFormError);

  if (error !== false) {
    console.warn(`${label} Error: ${error.message}`);
  }

  return (
    <FormControl
      mx={2}
      d="flex"
      w="100%"
      maxW="100%"
      flexDir="column"
      my={{ base: 2, lg: 4 }}
      isInvalid={error !== false}
      flex={{ base: '1 0 100%', lg: '1 0 33.33%' }}
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
        color={error !== false ? errorColor : labelColor}
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
      <FormErrorMessage opacity={opacity}>{error && error.message}</FormErrorMessage>
    </FormControl>
  );
};
