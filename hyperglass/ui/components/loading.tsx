import { Flex, Spinner } from '@chakra-ui/react';

import type { LoadableBaseOptions } from 'next/dynamic';

export const Loading: LoadableBaseOptions['loading'] = () => (
  <Flex flexDirection="column" minHeight="100vh" w="100%">
    <Flex
      px={2}
      py={0}
      w="100%"
      bg="white"
      color="black"
      flex="1 1 auto"
      textAlign="center"
      alignItems="center"
      justifyContent="center"
      flexDirection="column"
      css={{
        '@media (prefers-color-scheme: dark)': { backgroundColor: 'black', color: 'white' },
      }}
    >
      <Spinner color="primary.500" w="6rem" h="6rem" />
    </Flex>
  </Flex>
);
