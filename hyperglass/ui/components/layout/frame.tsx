import { useRef } from 'react';
import { Flex } from '@chakra-ui/react';
import { useConfig, useColorValue, useGlobalState } from '~/context';
import { If, Debugger, Greeting, Footer, Header } from '~/components';
import { useGreeting } from '~/hooks';

import type { TFrame } from './types';

export const Frame = (props: TFrame) => {
  const { web, developer_mode } = useConfig();
  const { isSubmitting, formData } = useGlobalState();
  const [greetingAck, setGreetingAck] = useGreeting();

  const bg = useColorValue('white', 'black');
  const color = useColorValue('black', 'white');

  const containerRef = useRef<HTMLDivElement>({} as HTMLDivElement);

  function resetForm(): void {
    containerRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    isSubmitting.set(false);
    formData.set({ query_location: [], query_target: '', query_type: '', query_vrf: '' });
    return;
  }

  return (
    <>
      <Flex bg={bg} w="100%" color={color} flexDir="column" minHeight="100vh" ref={containerRef}>
        <Flex px={2} flex="0 1 auto" flexDirection="column">
          <Header resetForm={resetForm} />
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
      <If c={web.greeting.enable && !greetingAck}>
        <Greeting onClickThrough={setGreetingAck} />
      </If>
    </>
  );
};
