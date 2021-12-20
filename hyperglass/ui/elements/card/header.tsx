import { Flex, Text } from '@chakra-ui/react';
import { useColorValue } from '~/hooks';

import type { FlexProps } from '@chakra-ui/react';

export const CardHeader = (props: FlexProps): JSX.Element => {
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
