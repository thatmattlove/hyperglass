import * as React from 'react';
import { Flex, Text, useColorMode } from '@chakra-ui/core';

const bg = { light: 'blackAlpha.50', dark: 'whiteAlpha.100' };

export const CardHeader = ({ children, ...props }) => {
  const { colorMode } = useColorMode();
  return (
    <Flex
      bg={bg[colorMode]}
      p={4}
      direction="column"
      roundedTopLeft={4}
      roundedTopRight={4}
      borderBottomWidth="1px"
      {...props}>
      <Text fontWeight="bold">{children}</Text>
    </Flex>
  );
};
