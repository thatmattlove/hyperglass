import * as React from 'react';
import { Box, useColorMode } from '@chakra-ui/core';

export const CodeBlock = ({ children }) => {
  const { colorMode } = useColorMode();
  const bg = { dark: 'gray.800', light: 'blackAlpha.100' };
  const color = { dark: 'white', light: 'black' };
  return (
    <Box
      fontFamily="mono"
      mt={5}
      p={3}
      border="1px"
      borderColor="inherit"
      rounded="md"
      bg={bg[colorMode]}
      color={color[colorMode]}
      fontSize="sm"
      whiteSpace="pre-wrap"
      as="pre">
      {children}
    </Box>
  );
};
