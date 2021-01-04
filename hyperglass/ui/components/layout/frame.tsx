import { useRef } from 'react';
import { Flex } from '@chakra-ui/react';
import { isSafari } from 'react-device-detect';
import { If, Debugger, Greeting, Footer, Header } from '~/components';
import { useConfig, useColorValue } from '~/context';
import { useLGState, useLGMethods } from '~/hooks';
import { ResetButton } from './resetButton';

import type { TFrame } from './types';

export const Frame: React.FC<TFrame> = (props: TFrame) => {
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
        color={color}
        flex="1 0 auto"
        flexDir="column"
        id="__hyperglass"
        ref={containerRef}
        /** minHeight
         * This is a Safari-specific fix. Without it, the footer will appear to be "under" the
         * viewport. Safari needs `-webkit-fill-available`, but other browsers need `100vh`.
         * @see https://allthingssmitty.com/2020/05/11/css-fix-for-100vh-in-mobile-webkit/
         */
        minHeight={isSafari ? '-webkit-fill-available' : '100vh'}
      >
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
