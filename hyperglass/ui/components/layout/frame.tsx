import { useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import { Flex } from '@chakra-ui/react';
import { isSafari } from 'react-device-detect';
import { If, Debugger, Greeting, Footer, Header } from '~/components';
import { useConfig } from '~/context';
import { useLGState, useLGMethods, useGoogleAnalytics } from '~/hooks';
import { ResetButton } from './resetButton';

import type { TFrame } from './types';

export const Frame = (props: TFrame): JSX.Element => {
  const router = useRouter();
  const { developerMode, googleAnalytics } = useConfig();
  const { isSubmitting } = useLGState();
  const { resetForm } = useLGMethods();
  const { initialize, trackPage } = useGoogleAnalytics();

  const containerRef = useRef<HTMLDivElement>({} as HTMLDivElement);

  function handleReset(): void {
    containerRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    isSubmitting.set(false);
    resetForm();
  }

  useEffect(() => {
    initialize(googleAnalytics, developerMode);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    trackPage(router.pathname);
  }, [router.pathname, trackPage]);

  return (
    <>
      <Flex
        w="100%"
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
          px={4}
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
        <If c={developerMode}>
          <Debugger />
        </If>
        <ResetButton developerMode={developerMode} resetForm={handleReset} />
      </Flex>
      <Greeting />
    </>
  );
};
