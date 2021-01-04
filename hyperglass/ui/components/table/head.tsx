import { Box } from '@chakra-ui/react';
import { useColorValue } from '~/context';

import type { BoxProps } from '@chakra-ui/react';

export const TableHead: React.FC<BoxProps> = (props: BoxProps) => {
  const bg = useColorValue('blackAlpha.100', 'whiteAlpha.100');
  return <Box as="thead" overflowX="hidden" overflowY="auto" bg={bg} {...props} />;
};
