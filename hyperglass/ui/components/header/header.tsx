import { Flex } from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedDiv, Title, ResetButton, ColorModeToggle } from '~/components';
import { useColorValue, useConfig, useBreakpointValue } from '~/context';
import { useBooleanValue, useLGState } from '~/hooks';

import type { ResponsiveValue } from '@chakra-ui/react';
import type { THeader, TTitleMode, THeaderLayout } from './types';

const headerTransition = {
  type: 'spring',
  ease: 'anticipate',
  damping: 15,
  stiffness: 100,
};

function getWidth(mode: TTitleMode): ResponsiveValue<string> {
  let width = '100%' as ResponsiveValue<string>;

  switch (mode) {
    case 'text_only':
      width = '100%';
      break;
    case 'logo_only':
      width = { base: '90%', lg: '50%' };
      break;
    case 'logo_subtitle':
      width = { base: '90%', lg: '50%' };
      break;
    case 'all':
      width = { base: '90%', lg: '50%' };
      break;
  }
  return width;
}

export const Header = (props: THeader) => {
  const { resetForm, ...rest } = props;
  const bg = useColorValue('white', 'black');

  const { web } = useConfig();
  const { isSubmitting } = useLGState();

  const mlResetButton = useBooleanValue(isSubmitting.value, { base: 0, md: 2 }, undefined);
  const titleHeight = useBooleanValue(isSubmitting.value, undefined, { md: '20vh' });

  const titleVariant = useBreakpointValue({
    base: {
      fullSize: { scale: 1, marginLeft: 0 },
      smallLogo: { marginLeft: 'auto' },
      smallText: { marginLeft: 'auto' },
    },
    md: {
      fullSize: { scale: 1 },
      smallLogo: { scale: 0.5 },
      smallText: { scale: 0.8 },
    },
    lg: {
      fullSize: { scale: 1 },
      smallLogo: { scale: 0.5 },
      smallText: { scale: 0.8 },
    },
    xl: {
      fullSize: { scale: 1 },
      smallLogo: { scale: 0.5 },
      smallText: { scale: 0.8 },
    },
  });

  const titleJustify = useBooleanValue(
    isSubmitting.value,
    { base: 'flex-end', md: 'center' },
    { base: 'flex-start', md: 'center' },
  );
  const resetButton = (
    <AnimatePresence key="resetButton">
      <AnimatedDiv
        transition={headerTransition}
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0, width: 'unset' }}
        exit={{ opacity: 0, x: -50 }}
        alignItems="center"
        mb={{ md: 'auto' }}
        ml={mlResetButton}
        display={isSubmitting ? 'flex' : 'none'}>
        <motion.div>
          <ResetButton onClick={resetForm} />
        </motion.div>
      </AnimatedDiv>
    </AnimatePresence>
  );
  const title = (
    <AnimatedDiv
      key="title"
      px={1}
      alignItems={isSubmitting ? 'center' : ['center', 'center', 'flex-end', 'flex-end']}
      transition={headerTransition}
      initial={{ scale: 0.5 }}
      animate={
        isSubmitting && web.text.title_mode === 'text_only'
          ? 'smallText'
          : isSubmitting && web.text.title_mode !== 'text_only'
          ? 'smallLogo'
          : 'fullSize'
      }
      variants={titleVariant}
      justifyContent={titleJustify}
      mt={[null, isSubmitting ? null : 'auto']}
      maxW={getWidth(web.text.title_mode)}
      flex="1 0 0"
      minH={titleHeight}>
      <Title onClick={resetForm} />
    </AnimatedDiv>
  );
  const colorModeToggle = (
    <AnimatedDiv
      transition={headerTransition}
      key="colorModeToggle"
      alignItems="center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      mb={[null, 'auto']}
      mr={isSubmitting ? undefined : 2}>
      <ColorModeToggle />
    </AnimatedDiv>
  );

  const layout = useBooleanValue(
    isSubmitting.value,
    {
      sm: [resetButton, colorModeToggle, title],
      md: [resetButton, title, colorModeToggle],
      lg: [resetButton, title, colorModeToggle],
      xl: [resetButton, title, colorModeToggle],
    },
    {
      sm: [title, resetButton, colorModeToggle],
      md: [resetButton, title, colorModeToggle],
      lg: [resetButton, title, colorModeToggle],
      xl: [resetButton, title, colorModeToggle],
    },
  ) as THeaderLayout;

  const layoutBp: keyof THeaderLayout =
    useBreakpointValue({ base: 'sm', md: 'md', lg: 'lg', xl: 'xl' }) ?? 'sm';

  return (
    <Flex
      px={2}
      zIndex="4"
      as="header"
      width="full"
      flex="0 1 auto"
      bg={bg}
      color="gray.500"
      {...rest}>
      <Flex
        w="100%"
        mx="auto"
        pt={6}
        justify="space-between"
        flex="1 0 auto"
        alignItems={isSubmitting ? 'center' : 'flex-start'}>
        {layout[layoutBp]}
      </Flex>
    </Flex>
  );
};
