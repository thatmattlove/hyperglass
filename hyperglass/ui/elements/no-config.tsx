import { Center, Flex, ChakraProvider, extendTheme } from '@chakra-ui/react';
import { mode } from '@chakra-ui/theme-tools';

import type { CenterProps } from '@chakra-ui/react';
import type { StyleFunctionProps } from '@chakra-ui/theme-tools';

const theme = extendTheme({
  useSystemColorMode: true,
  styles: {
    global: (props: StyleFunctionProps) => ({
      html: { scrollBehavior: 'smooth', height: '-webkit-fill-available' },
      body: {
        background: mode('white', 'black')(props),
        color: mode('black', 'white')(props),
        overflowX: 'hidden',
      },
    }),
  },
});

export const NoConfig = (props: CenterProps): JSX.Element => {
  return (
    <ChakraProvider theme={theme}>
      <Flex flexDirection="column" minHeight="100vh" w="100%">
        <Center flex="1 1 auto" {...props} />
      </Flex>
    </ChakraProvider>
  );
};
