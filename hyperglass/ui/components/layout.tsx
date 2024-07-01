import { Flex } from '@chakra-ui/react';
import { useCallback, useRef } from 'react';
import { isSafari } from 'react-device-detect';
import { If, Then } from 'react-if';
import { Debugger, Footer, Greeting, Header, ResetButton } from '~/components';
import { useConfig } from '~/context';
import { motionChakra } from '~/elements';
import { useFormState } from '~/hooks';

import type { FlexProps } from '@chakra-ui/react';

const Main = motionChakra('main', {
  baseStyle: {
    px: 4,
    py: 0,
    w: '100%',
    display: 'flex',
    flex: '1 1 auto',
    flexDir: 'column',
    textAlign: 'center',
    alignItems: 'center',
    justifyContent: 'start',
  },
});

export const Layout = (props: FlexProps): JSX.Element => {
  const { developerMode } = useConfig();
  const { setStatus, reset } = useFormState(
    useCallback(({ setStatus, reset }) => ({ setStatus, reset }), []),
  );

  const containerRef = useRef<HTMLDivElement>({} as HTMLDivElement);

  async function handleReset() {
    containerRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setStatus('form');
    reset();
  }

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
        <Header />
        <Main
          layout
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          exit={{ opacity: 0, x: -300 }}
          initial={{ opacity: 0, y: 300 }}
        >
          {props.children}
        </Main>
        <Footer />
        <If condition={developerMode}>
          <Then>
            <Debugger />
          </Then>
        </If>
        <ResetButton developerMode={developerMode} resetForm={handleReset} />
      </Flex>
      <Greeting />
    </>
  );
};
