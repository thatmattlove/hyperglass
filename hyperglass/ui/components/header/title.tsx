import { Flex, Button, VStack } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { isSafari } from 'react-device-detect';
import { If } from '~/components';
import { useConfig, useMobile } from '~/context';
import { useBooleanValue, useLGState, useLGMethods } from '~/hooks';
import { SubtitleOnly } from './subtitleOnly';
import { TitleOnly } from './titleOnly';
import { Logo } from './logo';

import type { TTitle, TTitleWrapper, TDWrapper, TMWrapper } from './types';

const AnimatedVStack = motion.custom(VStack);

/**
 * Title wrapper for mobile devices, breakpoints sm & md.
 */
const MWrapper: React.FC<TMWrapper> = (props: TMWrapper) => {
  const { isSubmitting } = useLGState();
  return (
    <AnimatedVStack
      layout
      spacing={1}
      alignItems={isSubmitting.value ? 'center' : 'flex-start'}
      {...props}
    />
  );
};

/**
 * Title wrapper for desktop devices, breakpoints lg & xl.
 */
const DWrapper: React.FC<TDWrapper> = (props: TDWrapper) => {
  const { isSubmitting } = useLGState();
  return (
    <AnimatedVStack
      spacing={1}
      initial="main"
      alignItems="center"
      animate={isSubmitting.value ? 'submitting' : 'main'}
      transition={{ damping: 15, type: 'spring', stiffness: 100 }}
      variants={{ submitting: { scale: 0.5 }, main: { scale: 1 } }}
      {...props}
    />
  );
};

/**
 * Universal wrapper for title sub-components, which will be different depending on the
 * `title_mode` configuration variable.
 */
const TitleWrapper: React.FC<TDWrapper | TMWrapper> = (props: TDWrapper | TMWrapper) => {
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
const TextOnly: React.FC<TTitleWrapper> = (props: TTitleWrapper) => {
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
const LogoOnly: React.FC = () => (
  <TitleWrapper>
    <Logo />
  </TitleWrapper>
);

/**
 * Title sub-component if `title_mode` is set to `logo_subtitle`. Renders the logo with the
 * subtitle underneath.
 */
const LogoSubtitle: React.FC = () => (
  <TitleWrapper>
    <Logo />
    <SubtitleOnly />
  </TitleWrapper>
);

/**
 * Title sub-component if `title_mode` is set to `all`. Renders the logo, title, and subtitle.
 */
const All: React.FC = () => (
  <TitleWrapper>
    <Logo />
    <TextOnly mt={2} />
  </TitleWrapper>
);

/**
 * Title component which renders sub-components based on the `title_mode` configuration variable.
 */
export const Title: React.FC<TTitle> = (props: TTitle) => {
  const { fontSize, ...rest } = props;
  const { web } = useConfig();
  const titleMode = web.text.title_mode;

  const { isSubmitting } = useLGState();
  const { resetForm } = useLGMethods();

  const titleHeight = useBooleanValue(isSubmitting.value, undefined, { md: '20vh' });

  function handleClick(): void {
    isSubmitting.set(false);
    resetForm();
  }

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
      mt={[null, isSubmitting.value ? null : 'auto']}
      {...rest}
    >
      <Button
        px={0}
        variant="link"
        flexWrap="wrap"
        flexDir="column"
        onClick={handleClick}
        _focus={{ boxShadow: 'none' }}
        _hover={{ textDecoration: 'none' }}
      >
        <If c={titleMode === 'text_only'}>
          <TextOnly />
        </If>
        <If c={titleMode === 'logo_only'}>
          <LogoOnly />
        </If>
        <If c={titleMode === 'logo_subtitle'}>
          <LogoSubtitle />
        </If>
        <If c={titleMode === 'all'}>
          <All />
        </If>
      </Button>
    </Flex>
  );
};
