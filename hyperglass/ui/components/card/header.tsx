import { Flex, Text } from '@chakra-ui/react';
import { useColorValue } from '~/context';

import type { TCardHeader } from './types';

export const CardHeader: React.FC<TCardHeader> = (props: TCardHeader) => {
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
      {...rest}
    >
      <Text fontWeight="bold">{children}</Text>
    </Flex>
  );
};
