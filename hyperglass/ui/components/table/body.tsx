import { Box } from '@chakra-ui/react';

import type { BoxProps } from '@chakra-ui/react';

export const TableBody: React.FC<BoxProps> = (props: BoxProps) => (
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
