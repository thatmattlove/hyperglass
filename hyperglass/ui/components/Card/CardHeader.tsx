import { Flex, Text } from '@chakra-ui/core';
import { useColorValue } from '~/context';

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
