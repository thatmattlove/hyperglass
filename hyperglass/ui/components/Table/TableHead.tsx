import { Box } from '@chakra-ui/core';
import { useColorValue } from '~/context';

import type { BoxProps } from '@chakra-ui/core';

export const TableHead = (props: BoxProps) => {
  const bg = useColorValue('blackAlpha.100', 'whiteAlpha.100');
  return <Box as="thead" overflowX="hidden" overflowY="auto" bg={bg} {...props} />;
};
