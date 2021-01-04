import { useMemo } from 'react';
import { useRouter } from 'next/router';
import {
  Flex,
  Text,
  theme,
  Button,
  Heading,
  ThemeProvider,
  ChakraProvider,
  useColorModeValue,
} from '@chakra-ui/react';
import { inRange } from 'lodash';

import type { NextPage, NextPageContext } from 'next';

interface TError {
  status: string;
  code: number;
}

const ErrorContent: React.FC<TError> = (props: TError) => {
  const { status, code } = props;
  const router = useRouter();

  const bg = useColorModeValue('white', 'black');
  const color = useColorModeValue('black', 'white');
  const error400 = useColorModeValue('error.500', 'error.300');
  const error500 = useColorModeValue('danger.500', 'danger.300');
  const errorColor = { 400: error400, 500: error500 };
  const colorScheme = { 400: 'error', 500: 'danger' };

  const baseCode = useMemo(() => {
    return inRange(code, 400, 500) ? 400 : inRange(code, 500, 600) ? 500 : 400;
  }, [code]);

  function handleClick(): void {
    router.push('/');
  }

  return (
    <Flex w="100%" minHeight="100vh" bg={bg} flexDirection="column" color={color}>
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
        mt={{ base: '50%', xl: '25%' }}
      >
        <Heading mb={4} as="h1" fontSize="2xl">
          <Text as="span" color={errorColor[baseCode]}>
            {status}
          </Text>
          {code === 404 && <Text as="span">{` isn't a thing...`}</Text>}
        </Heading>
        <Button variant="outline" onClick={handleClick} colorScheme={colorScheme[baseCode]}>
          Home
        </Button>
      </Flex>
    </Flex>
  );
};

const ErrorPage: NextPage<TError> = (props: TError) => {
  const { status, code } = props;
  return (
    <ThemeProvider theme={theme}>
      <ChakraProvider>
        <ErrorContent status={status} code={code} />
      </ChakraProvider>
    </ThemeProvider>
  );
};

ErrorPage.getInitialProps = (ctx: NextPageContext): TError => {
  const { res, err } = ctx;
  const code = res ? res.statusCode : err ? err.statusCode ?? 500 : 404;
  const status = err ? err.message : 'Error';
  return { status, code };
};

export default ErrorPage;
