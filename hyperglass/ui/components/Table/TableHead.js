import * as React from 'react';
import { Box, useColorMode } from '@chakra-ui/core';

const bg = { dark: 'whiteAlpha.100', light: 'blackAlpha.100' };

export const TableHead = ({ children, ...props }) => {
  const { colorMode } = useColorMode();
  return (
    <Box as="thead" overflowX="hidden" overflowY="auto" bg={bg[colorMode]} {...props}>
      {children}
    </Box>
  );
};
