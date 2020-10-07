import * as React from 'react';
import { Flex, FormControl, FormLabel, FormErrorMessage, useColorMode } from '@chakra-ui/core';

const labelColor = { dark: 'whiteAlpha.700', light: 'blackAlpha.700' };

export const FormField = ({
  label,
  name,
  error,
  hiddenLabels,
  helpIcon,
  targetInfo,
  setTarget,
  labelAddOn,
  fieldAddOn,
  children,
  ...props
}) => {
  const { colorMode } = useColorMode();

  return (
    <FormControl
      as={Flex}
      flexDirection="column"
      flex={['1 0 100%', '1 0 100%', '1 0 33.33%', '1 0 33.33%']}
      w="100%"
      maxW="100%"
      mx={2}
      my={[2, 2, 4, 4]}
      isInvalid={error && error.message}
      {...props}>
      <FormLabel
        htmlFor={name}
        color={labelColor[colorMode]}
        pl={1}
        opacity={hiddenLabels ? 0 : null}
        display="flex"
        alignItems="center"
        justifyContent="space-between"
        pr={0}>
        {label}
        {labelAddOn || null}
      </FormLabel>
      {children}
      {fieldAddOn && (
        <Flex justifyContent="flex-end" pt={3}>
          {fieldAddOn}
        </Flex>
      )}
      <FormErrorMessage opacity={hiddenLabels ? 0 : null}>
        {error && error.message}
      </FormErrorMessage>
    </FormControl>
  );
};
