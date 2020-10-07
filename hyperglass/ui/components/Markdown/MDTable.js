import * as React from 'react';
import { Box, useColorMode } from '@chakra-ui/core';

export const Table = props => <Box as="table" textAlign="left" mt={4} width="full" {...props} />;

const bg = { light: 'blackAlpha.50', dark: 'whiteAlpha.50' };

export const TableHeader = props => {
  const { colorMode } = useColorMode();

  return <Box as="th" bg={bg[colorMode]} fontWeight="semibold" p={2} fontSize="sm" {...props} />;
};

export const TableCell = ({ isHeader = false, ...props }) => (
  <Box
    as={isHeader ? 'th' : 'td'}
    p={2}
    borderTopWidth="1px"
    borderColor="inherit"
    fontSize="sm"
    whiteSpace="normal"
    {...props}
  />
);
