import { Box } from '@chakra-ui/core';
import type { BoxProps } from '@chakra-ui/core';

export const TableBody = (props: BoxProps) => (
  <Box
    as="tbody"
    overflowY="scroll"
    css={{
      '&::-webkit-scrollbar': { display: 'none' },
      '&': { msOverflowStyle: 'none' },
    }}
    overflowX="hidden"
    {...props}
  />
);
