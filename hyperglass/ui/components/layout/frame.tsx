import { useRef } from 'react';
import { Flex } from '@chakra-ui/react';
import { useConfig, useColorValue } from '~/context';
import { If, Debugger, Greeting, Footer, Header } from '~/components';
import { useLGState } from '~/hooks';

import type { TFrame } from './types';

export const Frame = (props: TFrame) => {
  const { developer_mode } = useConfig();
  const { isSubmitting, resetForm } = useLGState();

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
      <Flex bg={bg} w="100%" color={color} flexDir="column" minHeight="100vh" ref={containerRef}>
        <Flex px={2} flex="0 1 auto" flexDirection="column">
          <Header resetForm={handleReset} />
        </Flex>
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
      </Flex>
      <Greeting />
    </>
  );
};
