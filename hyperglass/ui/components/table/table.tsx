import { chakra } from '@chakra-ui/react';
import { useColorValue } from '~/hooks';

import type { BoxProps } from '@chakra-ui/react';

export const TableMain = (props: BoxProps): JSX.Element => {
  const scrollbar = useColorValue('blackAlpha.300', 'whiteAlpha.300');
  const scrollbarHover = useColorValue('blackAlpha.400', 'whiteAlpha.400');
  const scrollbarBg = useColorValue('blackAlpha.50', 'whiteAlpha.50');
  return (
    <chakra.table
      display="block"
      overflowX="auto"
      borderRadius="md"
      boxSizing="border-box"
      css={{
        '&::-webkit-scrollbar': { height: '5px' },
        '&::-webkit-scrollbar-track': {
          backgroundColor: scrollbarBg,
        },
        '&::-webkit-scrollbar-thumb': {
          backgroundColor: scrollbar,
        },
        '&::-webkit-scrollbar-thumb:hover': {
          backgroundColor: scrollbarHover,
        },

        '-ms-overflow-style': { display: 'none' },
      }}
      {...props}
    />
  );
};
