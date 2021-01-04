import { Box } from '@chakra-ui/react';
import { useColorValue } from '~/context';

import type { BoxProps } from '@chakra-ui/react';

export const TableMain: React.FC<BoxProps> = (props: BoxProps) => {
  const scrollbar = useColorValue('blackAlpha.300', 'whiteAlpha.300');
  const scrollbarHover = useColorValue('blackAlpha.400', 'whiteAlpha.400');
  const scrollbarBg = useColorValue('blackAlpha.50', 'whiteAlpha.50');
  return (
    <Box
      as="table"
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
