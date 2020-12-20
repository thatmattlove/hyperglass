import { forwardRef } from 'react';
import { Button, Stack } from '@chakra-ui/react';
import { If } from '~/components';
import { useConfig } from '~/context';
import { useBooleanValue, useLGState } from '~/hooks';
import { TitleOnly } from './titleOnly';
import { SubtitleOnly } from './subtitleOnly';
import { Logo } from './logo';

import type { TTitle, TTextOnly } from './types';

const TextOnly = (props: TTextOnly) => {
  const { showSubtitle, ...rest } = props;

  return (
    <Stack
      spacing={2}
      maxW="100%"
      textAlign={showSubtitle ? ['right', 'center'] : ['left', 'center']}
      {...rest}>
      <TitleOnly showSubtitle={showSubtitle} />
      <If c={showSubtitle}>
        <SubtitleOnly />
      </If>
    </Stack>
  );
};

const LogoSubtitle = () => (
  <>
    <Logo />
    <SubtitleOnly mt={6} />
  </>
);

const All = (props: TTextOnly) => {
  const { showSubtitle, ...rest } = props;
  return (
    <>
      <Logo />
      <TextOnly showSubtitle={showSubtitle} mt={2} {...rest} />
    </>
  );
};

export const Title = forwardRef<HTMLButtonElement, TTitle>((props, ref) => {
  const { web } = useConfig();
  const titleMode = web.text.title_mode;

  const { isSubmitting } = useLGState();

  const justify = useBooleanValue(
    isSubmitting.value,
    { base: 'flex-end', md: 'center' },
    { base: 'flex-start', md: 'center' },
  );

  return (
    <Button
      px={0}
      w="100%"
      ref={ref}
      variant="link"
      flexWrap="wrap"
      flexDir="column"
      justifyContent={justify}
      _focus={{ boxShadow: 'none' }}
      _hover={{ textDecoration: 'none' }}
      alignItems={{ base: 'flex-start', lg: 'center' }}
      {...props}>
      <If c={titleMode === 'text_only'}>
        <TextOnly showSubtitle={!isSubmitting.value} />
      </If>
      <If c={titleMode === 'logo_only'}>
        <Logo />
      </If>
      <If c={titleMode === 'logo_subtitle'}>
        <LogoSubtitle />
      </If>
      <If c={titleMode === 'all'}>
        <All showSubtitle={!isSubmitting.value} />
      </If>
    </Button>
  );
});
