import React from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/router';
import {
  Button,
  CSSReset,
  Flex,
  Heading,
  Text,
  ThemeProvider,
  useColorMode,
  theme as defaultTheme,
} from '@chakra-ui/core';
import { inRange } from 'lodash';

const ColorModeProvider = dynamic(
  () => import('@chakra-ui/core').then(mod => mod.ColorModeProvider),
  { ssr: false },
);

const ErrorContent = ({ msg, statusCode }) => {
  const { colorMode } = useColorMode();
  const bg = { light: 'white', dark: 'black' };
  const baseCode = inRange(statusCode, 400, 500) ? 400 : inRange(statusCode, 500, 600) ? 500 : 400;
  const errorColor = {
    400: { light: 'error.500', dark: 'error.300' },
    500: { light: 'danger.500', dark: 'danger.300' },
  };
  const variantColor = {
    400: 'error',
    500: 'danger',
  };
  const color = { light: 'black', dark: 'white' };
  const { push } = useRouter();
  const handleClick = () => push('/');
  return (
    <Flex
      w="100%"
      minHeight="100vh"
      bg={bg[colorMode]}
      flexDirection="column"
      color={color[colorMode]}>
      <Flex
        px={2}
        py={0}
        w="100%"
        as="main"
        flexGrow={1}
        flexShrink={1}
        flexBasis="auto"
        textAlign="center"
        alignItems="center"
        flexDirection="column"
        justifyContent="start"
        mt={['50%', '50%', '50%', '25%']}>
        <Heading mb={4} as="h1" fontSize="2xl">
          <Text as="span" color={errorColor[baseCode][colorMode]}>
            {msg}
          </Text>
          {statusCode === 404 && <Text as="span"> isn't a thing...</Text>}
        </Heading>

        <Button variant="outline" onClick={handleClick} variantColor={variantColor[baseCode]}>
          Home
        </Button>
      </Flex>
    </Flex>
  );
};

const ErrorPage = ({ msg, statusCode }) => {
  return (
    <ThemeProvider theme={defaultTheme}>
      <ColorModeProvider>
        <CSSReset />
        <ErrorContent msg={msg} statusCode={statusCode} />
      </ColorModeProvider>
    </ThemeProvider>
  );
};

ErrorPage.getInitialProps = ({ res, err }) => {
  const statusCode = res ? res.statusCode : err ? err.statusCode : 404;
  const msg = err ? err.message : res.req?.url || 'Error';
  return { msg, statusCode };
};

export default ErrorPage;
