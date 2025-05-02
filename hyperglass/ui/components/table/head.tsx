import { chakra } from '@chakra-ui/react';
import { useColorValue } from '~/hooks';

import type { BoxProps } from '@chakra-ui/react';

export const TableHead = (props: BoxProps): JSX.Element => {
  const bg = useColorValue('blackAlpha.100', 'whiteAlpha.100');
  return <chakra.thead overflowX="hidden" overflowY="auto" bg={bg} {...props} />;
};
