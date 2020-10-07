import * as React from 'react';
import { Flex, useColorMode } from '@chakra-ui/core';

const bg = { light: 'white', dark: 'original.dark' };
const color = { light: 'original.dark', dark: 'white' };

export const CardBody = ({ onClick = () => false, children, ...props }) => {
  const { colorMode } = useColorMode();
  return (
    <Flex
      w="100%"
      maxW="100%"
      rounded="md"
      borderWidth="1px"
      direction="column"
      onClick={onClick}
      bg={bg[colorMode]}
      color={color[colorMode]}
      overflow="hidden"
      {...props}>
      {children}
    </Flex>
  );
};
