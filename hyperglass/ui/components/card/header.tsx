import { Flex, Text } from '@chakra-ui/react';
import { useColorValue } from '~/context';

import type { ICardHeader } from './types';

export const CardHeader = (props: ICardHeader) => {
  const { children, ...rest } = props;
  const bg = useColorValue('blackAlpha.50', 'whiteAlpha.100');
  return (
    <Flex
      p={4}
      bg={bg}
      direction="column"
      roundedTopLeft={4}
      roundedTopRight={4}
      borderBottomWidth="1px"
      {...rest}>
      <Text fontWeight="bold">{children}</Text>
    </Flex>
  );
};
