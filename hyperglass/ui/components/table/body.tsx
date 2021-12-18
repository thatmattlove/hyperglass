import { chakra } from '@chakra-ui/react';

import type { BoxProps } from '@chakra-ui/react';

export const TableBody = (props: BoxProps): JSX.Element => (
  <chakra.tbody
    overflowY="scroll"
    css={{
      '&::-webkit-scrollbar': { display: 'none' },
      '&': { msOverflowStyle: 'none' },
    }}
    overflowX="hidden"
    {...props}
  />
);
