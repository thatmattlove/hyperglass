import { Flex, Button, VStack } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { isSafari } from 'react-device-detect';
import { Switch, Case } from 'react-if';
import { useConfig, useMobile } from '~/context';
import { useBooleanValue, useFormState } from '~/hooks';
import { SubtitleOnly } from './subtitleOnly';
import { TitleOnly } from './titleOnly';
import { Logo } from './logo';

import type { TTitle, TTitleWrapper, TDWrapper, TMWrapper } from './types';

const AnimatedVStack = motion(VStack);

/**
 * Title wrapper for mobile devices, breakpoints sm & md.
 */
const MWrapper = (props: TMWrapper): JSX.Element => {
  const status = useFormState(s => s.status);
  return (
    <AnimatedVStack
      layout
      spacing={1}
      alignItems={status === 'results' ? 'center' : 'flex-start'}
      {...props}
    />
  );
};

/**
 * Title wrapper for desktop devices, breakpoints lg & xl.
 */
const DWrapper = (props: TDWrapper): JSX.Element => {
  const status = useFormState(s => s.status);
  return (
    <AnimatedVStack
      spacing={1}
      initial="main"
      alignItems="center"
      animate={status}
      transition={{ damping: 15, type: 'spring', stiffness: 100 }}
      variants={{ results: { scale: 0.5 }, form: { scale: 1 } }}
      {...props}
    />
  );
};

/**
 * Universal wrapper for title sub-components, which will be different depending on the
 * `title_mode` configuration variable.
 */
const TitleWrapper = (props: TDWrapper | TMWrapper): JSX.Element => {
  const isMobile = useMobile();
  return (
    <>
      {isMobile ? <MWrapper {...(props as TMWrapper)} /> : <DWrapper {...(props as TDWrapper)} />}
    </>
  );
};

/**
 * Title sub-component if `title_mode` is set to `text_only`.
 */
const TextOnly = (props: TTitleWrapper): JSX.Element => {
  return (
    <TitleWrapper {...props}>
      <TitleOnly />
      <SubtitleOnly />
    </TitleWrapper>
  );
};

/**
 * Title sub-component if `title_mode` is set to `logo_only`. Renders only the logo.
 */
const LogoOnly = (): JSX.Element => (
  <TitleWrapper>
    <Logo />
  </TitleWrapper>
);

/**
 * Title sub-component if `title_mode` is set to `logo_subtitle`. Renders the logo with the
 * subtitle underneath.
 */
const LogoSubtitle = (): JSX.Element => (
  <TitleWrapper>
    <Logo />
    <SubtitleOnly />
  </TitleWrapper>
);

/**
 * Title sub-component if `title_mode` is set to `all`. Renders the logo, title, and subtitle.
 */
const All = (): JSX.Element => (
  <TitleWrapper>
    <Logo />
    <TextOnly mt={2} />
  </TitleWrapper>
);

/**
 * Title component which renders sub-components based on the `title_mode` configuration variable.
 */
export const Title = (props: TTitle): JSX.Element => {
  const { fontSize, ...rest } = props;
  const { web } = useConfig();
  const { titleMode } = web.text;

  const { status, reset } = useFormState(({ status, reset }) => ({
    status,
    reset,
  }));

  const titleHeight = useBooleanValue(status === 'results', undefined, { md: '20vh' });

  return (
    <Flex
      px={0}
      flexWrap="wrap"
      flexDir="column"
      minH={titleHeight}
      justifyContent="center"
      /* flexBasis
        This is a fix for Safari specifically. LMGTFY: Safari flex-basis width. Nutshell: Safari
        is stupid, in that it infers the default flex-basis from the width, 100%. Other browsers
        don't do this. Without the below fix, the logo will appear gigantic, filling the entire
        div up to the parent's max-width. The fix is to hard-code a flex-basis width.
       */
      flexBasis={{ base: '100%', lg: isSafari ? '33%' : '100%' }}
      mt={{ md: status === 'results' ? undefined : 'auto' }}
      {...rest}
    >
      <Button
        px={0}
        variant="link"
        flexWrap="wrap"
        flexDir="column"
        onClick={() => reset()}
        _focus={{ boxShadow: 'none' }}
        _hover={{ textDecoration: 'none' }}
      >
        <Switch>
          <Case condition={titleMode === 'text_only'}>
            <TextOnly />
          </Case>
          <Case condition={titleMode === 'logo_only'}>
            <LogoOnly />
          </Case>
          <Case condition={titleMode === 'logo_subtitle'}>
            <LogoSubtitle />
          </Case>
          <Case condition={titleMode === 'all'}>
            <All />
          </Case>
        </Switch>
      </Button>
    </Flex>
  );
};
