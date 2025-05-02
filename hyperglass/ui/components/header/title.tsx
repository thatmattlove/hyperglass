import { Button, Flex, VStack } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { isSafari } from 'react-device-detect';
import { Case, Switch } from 'react-if';
import { useConfig } from '~/context';
import { useFormInteractive, useFormState, useMobile } from '~/hooks';
import { Logo } from './logo';
import { SubtitleOnly } from './subtitle-only';
import { TitleOnly } from './title-only';

import type { FlexProps, StackProps } from '@chakra-ui/react';
import type { MotionProps } from 'framer-motion';

type DWrapperProps = Omit<StackProps, 'transition'> & MotionProps;
type MWrapperProps = Omit<StackProps, 'transition'> & MotionProps;
type WrapperProps = Partial<MotionProps & Omit<StackProps, 'transition'>>;

const AnimatedVStack = motion(VStack);
const AnimatedFlex = motion(Flex);

/**
 * Title wrapper for mobile devices, breakpoints sm & md.
 */
const MWrapper = (props: MWrapperProps): JSX.Element => {
  const formInteractive = useFormInteractive();
  return (
    <AnimatedVStack
      layout
      spacing={1}
      alignItems={formInteractive ? 'center' : 'flex-start'}
      {...props}
    />
  );
};

/**
 * Title wrapper for desktop devices, breakpoints lg & xl.
 */
const DWrapper = (props: DWrapperProps): JSX.Element => {
  const formInteractive = useFormInteractive();
  return (
    <AnimatedVStack
      spacing={1}
      initial="main"
      alignItems="center"
      animate={formInteractive}
      transition={{ damping: 15, type: 'spring', stiffness: 100 }}
      variants={{ results: { scale: 0.5 }, form: { scale: 1 } }}
      maxWidth="75%"
      {...props}
    />
  );
};

/**
 * Universal wrapper for title sub-components, which will be different depending on the
 * `title_mode` configuration variable.
 */
const TitleWrapper = (props: DWrapperProps | MWrapperProps): JSX.Element => {
  const isMobile = useMobile();
  return (
    <>
      {isMobile ? (
        <MWrapper {...(props as MWrapperProps)} />
      ) : (
        <DWrapper {...(props as DWrapperProps)} />
      )}
    </>
  );
};

/**
 * Title sub-component if `title_mode` is set to `text_only`.
 */
const TextOnly = (props: WrapperProps): JSX.Element => {
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
const LogoOnly = (props: WrapperProps): JSX.Element => (
  <TitleWrapper {...props}>
    <Logo />
  </TitleWrapper>
);

/**
 * Title sub-component if `title_mode` is set to `logo_subtitle`. Renders the logo with the
 * subtitle underneath.
 */
const LogoSubtitle = (props: WrapperProps): JSX.Element => (
  <TitleWrapper {...props}>
    <Logo />
    <SubtitleOnly />
  </TitleWrapper>
);

/**
 * Title sub-component if `title_mode` is set to `all`. Renders the logo, title, and subtitle.
 */
const All = (props: WrapperProps): JSX.Element => (
  <TitleWrapper {...props}>
    <Logo />
    <TextOnly mt={2} />
  </TitleWrapper>
);

/**
 * Title component which renders sub-components based on the `title_mode` configuration variable.
 */
export const Title = (props: FlexProps): JSX.Element => {
  const { fontSize, ...rest } = props;
  const { web } = useConfig();
  const { titleMode } = web.text;

  const reset = useFormState(s => s.reset);
  const formInteractive = useFormInteractive();

  return (
    <AnimatedFlex
      px={0}
      flexWrap="wrap"
      flexDir="column"
      animate={{ height: formInteractive ? undefined : '20vh' }}
      justifyContent="center"
      /* flexBasis
        This is a fix for Safari specifically. LMGTFY: Safari flex-basis width. Nutshell: Safari
        is stupid, in that it infers the default flex-basis from the width, 100%. Other browsers
        don't do this. Without the below fix, the logo will appear gigantic, filling the entire
        div up to the parent's max-width. The fix is to hard-code a flex-basis width.
       */
      flexBasis={{ base: '100%', lg: isSafari ? '33%' : '100%' }}
      mt={{ md: formInteractive ? undefined : 'auto' }}
      {...rest}
    >
      <Button
        px={0}
        variant="link"
        flexWrap="wrap"
        flexDir="column"
        onClick={async () => await reset()}
        _focus={{ boxShadow: 'none' }}
        _hover={{ textDecoration: 'none' }}
      >
        <Switch>
          <Case condition={titleMode === 'text_only'}>
            <TextOnly width={web.logo.width} />
          </Case>
          <Case condition={titleMode === 'logo_only'}>
            <LogoOnly width={web.logo.width} />
          </Case>
          <Case condition={titleMode === 'logo_subtitle'}>
            <LogoSubtitle width={web.logo.width} />
          </Case>
          <Case condition={titleMode === 'all'}>
            <All width={web.logo.width} />
          </Case>
        </Switch>
      </Button>
    </AnimatedFlex>
  );
};
