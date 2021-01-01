import { useRef } from 'react';
import { Flex } from '@chakra-ui/react';
import { If, Debugger, Greeting, Footer, Header } from '~/components';
import { useConfig, useColorValue } from '~/context';
import { useLGState, useLGMethods } from '~/hooks';
import { ResetButton } from './resetButton';

import type { TFrame } from './types';

export const Frame = (props: TFrame) => {
  const { developer_mode } = useConfig();
  const { isSubmitting } = useLGState();
  const { resetForm } = useLGMethods();

  const bg = useColorValue('white', 'black');
  const color = useColorValue('black', 'white');

  const containerRef = useRef<HTMLDivElement>({} as HTMLDivElement);

  function handleReset(): void {
    containerRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    isSubmitting.set(false);
    resetForm();
  }

  return (
    <>
      <Flex
        bg={bg}
        w="100%"
        id="__hyperglass"
        color={color}
        flexDir="column"
        minHeight="100vh"
        ref={containerRef}>
        <Header resetForm={handleReset} />
        <Flex
          px={2}
          py={0}
          w="100%"
          as="main"
          align="center"
          flex="1 1 auto"
          justify="start"
          flexDir="column"
          textAlign="center"
          {...props}
        />
        <Footer />
        <If c={developer_mode}>
          <Debugger />
        </If>
        <ResetButton developerMode={developer_mode} resetForm={handleReset} />
      </Flex>
      <Greeting />
    </>
  );
};
