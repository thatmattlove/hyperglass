import * as React from 'react';
import { Flex, Spinner, useColorMode } from '@chakra-ui/core';

export const Loading = () => {
  const { colorMode } = useColorMode();
  const bg = { light: 'white', dark: 'black' };
  const color = { light: 'black', dark: 'white' };
  return (
    <Flex
      flexDirection="column"
      minHeight="100vh"
      w="100%"
      bg={bg[colorMode]}
      color={color[colorMode]}>
      <Flex
        as="main"
        w="100%"
        flexGrow={1}
        flexShrink={1}
        flexBasis="auto"
        alignItems="center"
        justifyContent="start"
        textAlign="center"
        flexDirection="column"
        px={2}
        py={0}
        mt={['50%', '50%', '50%', '25%']}>
        <Spinner color="primary.500" w="6rem" h="6rem" />
      </Flex>
    </Flex>
  );
};
