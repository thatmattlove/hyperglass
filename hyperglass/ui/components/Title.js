/** @jsx jsx */
import { jsx } from '@emotion/core';
import { forwardRef } from 'react';
import { Button, Heading, Image, Stack, useColorMode } from '@chakra-ui/core';
import { useConfig, useMedia } from 'app/context';

const titleSize = { true: ['2xl', '2xl', '5xl', '5xl'], false: '2xl' };
const titleMargin = { true: 2, false: 0 };
const textAlignment = { false: ['right', 'center'], true: ['left', 'center'] };
const logoName = { light: 'dark', dark: 'light' };
const justifyMap = {
  true: ['flex-end', 'center', 'center', 'center'],
  false: ['flex-start', 'center', 'center', 'center'],
};

const logoFallback = {
  light: 'https://res.cloudinary.com/hyperglass/image/upload/v1593916013/logo-dark.svg',
  dark: 'https://res.cloudinary.com/hyperglass/image/upload/v1593916013/logo-light.svg',
};

const TitleOnly = ({ text, showSubtitle }) => (
  <Heading as="h1" mb={titleMargin[showSubtitle]} fontSize={titleSize[showSubtitle]}>
    {text}
  </Heading>
);

const SubtitleOnly = ({ text, mediaSize, ...props }) => (
  <Heading
    as="h3"
    fontSize={['md', 'md', 'xl', 'xl']}
    whiteSpace="break-spaces"
    textAlign={['left', 'left', 'center', 'center']}
    {...props}>
    {text}
  </Heading>
);

const TextOnly = ({ text, mediaSize, showSubtitle, ...props }) => (
  <Stack spacing={2} maxW="100%" textAlign={textAlignment[showSubtitle]} {...props}>
    <TitleOnly text={text.title} showSubtitle={showSubtitle} />
    {showSubtitle && <SubtitleOnly text={text.subtitle} mediaSize={mediaSize} />}
  </Stack>
);

const Logo = ({ text, logo }) => {
  const { colorMode } = useColorMode();
  const { width, dark_format, light_format } = logo;
  const logoExt = { light: dark_format, dark: light_format };
  return (
    <Image
      css={{
        userDrag: 'none',
        userSelect: 'none',
        msUserSelect: 'none',
        MozUserSelect: 'none',
        WebkitUserDrag: 'none',
        WebkitUserSelect: 'none',
      }}
      alt={text.title}
      width={width ?? 'auto'}
      fallbackSrc={logoFallback[colorMode]}
      src={`/images/${logoName[colorMode]}${logoExt[colorMode]}`}
    />
  );
};

const LogoSubtitle = ({ text, logo, mediaSize }) => (
  <>
    <Logo text={text} logo={logo} mediaSize={mediaSize} />
    <SubtitleOnly mt={6} text={text.subtitle} />
  </>
);

const All = ({ text, logo, mediaSize, showSubtitle }) => (
  <>
    <Logo text={text} logo={logo} />
    <TextOnly mediaSize={mediaSize} showSubtitle={showSubtitle} mt={2} text={text} />
  </>
);

const modeMap = {
  text_only: TextOnly,
  logo_only: Logo,
  logo_subtitle: LogoSubtitle,
  all: All,
};

export const Title = forwardRef(({ onClick, isSubmitting, ...props }, ref) => {
  const { web } = useConfig();
  const { mediaSize } = useMedia();
  const titleMode = web.text.title_mode;
  const MatchedMode = modeMap[titleMode];
  return (
    <Button
      px={0}
      w="100%"
      ref={ref}
      variant="link"
      flexWrap="wrap"
      flexDir="column"
      onClick={onClick}
      _focus={{ boxShadow: 'none' }}
      _hover={{ textDecoration: 'none' }}
      justifyContent={justifyMap[isSubmitting]}
      alignItems={['flex-start', 'flex-start', 'center']}
      {...props}>
      <MatchedMode
        mediaSize={mediaSize}
        showSubtitle={!isSubmitting}
        text={web.text}
        logo={web.logo}
      />
    </Button>
  );
});
