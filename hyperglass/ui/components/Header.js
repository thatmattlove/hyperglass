import * as React from 'react';
import { Flex, useColorMode } from '@chakra-ui/core';
import { motion, AnimatePresence } from 'framer-motion';
import { useConfig, useHyperglassState, useMedia } from 'app/context';
import { Title, ResetButton, ColorModeToggle } from 'app/components';

const titleVariants = {
  sm: {
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
};

const bg = { light: 'white', dark: 'black' };
const headerTransition = {
  type: 'spring',
  ease: 'anticipate',
  damping: 15,
  stiffness: 100,
};
const titleJustify = {
  true: ['flex-end', 'flex-end', 'center', 'center'],
  false: ['flex-start', 'flex-start', 'center', 'center'],
};
const titleHeight = {
  true: null,
  false: [null, '20vh', '20vh', '20vh'],
};
const resetButtonMl = { true: [null, 2, 2, 2], false: null };

const widthMap = {
  text_only: '100%',
  logo_only: ['90%', '90%', '50%', '50%'],
  logo_subtitle: ['90%', '90%', '50%', '50%'],
  all: ['90%', '90%', '50%', '50%'],
};

export const Header = ({ layoutRef, ...props }) => {
  const AnimatedFlex = motion.custom(Flex);
  const AnimatedResetButton = motion.custom(ResetButton);
  const { colorMode } = useColorMode();
  const { web } = useConfig();
  const { mediaSize } = useMedia();
  const { isSubmitting, resetForm } = useHyperglassState();
  const handleFormReset = () => {
    resetForm(layoutRef);
  };
  const resetButton = (
    <AnimatePresence key="resetButton">
      <AnimatedFlex
        layoutTransition={headerTransition}
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0, width: 'unset' }}
        exit={{ opacity: 0, x: -50 }}
        alignItems="center"
        mb={[null, 'auto']}
        ml={resetButtonMl[isSubmitting]}
        display={isSubmitting ? 'flex' : 'none'}>
        <AnimatedResetButton isSubmitting={isSubmitting} onClick={handleFormReset} />
      </AnimatedFlex>
    </AnimatePresence>
  );
  const title = (
    <AnimatedFlex
      key="title"
      px={1}
      alignItems={isSubmitting ? 'center' : ['center', 'center', 'flex-end', 'flex-end']}
      positionTransition={headerTransition}
      initial={{ scale: 0.5 }}
      animate={
        isSubmitting && web.text.title_mode === 'text_only'
          ? 'smallText'
          : isSubmitting && web.text.title_mode !== 'text_only'
          ? 'smallLogo'
          : 'fullSize'
      }
      variants={titleVariants[mediaSize]}
      justifyContent={titleJustify[isSubmitting]}
      mt={[null, isSubmitting ? null : 'auto']}
      maxW={widthMap[web.text.title_mode]}
      flex="1 0 0"
      minH={titleHeight[isSubmitting]}>
      <Title isSubmitting={isSubmitting} onClick={handleFormReset} />
    </AnimatedFlex>
  );
  const colorModeToggle = (
    <AnimatedFlex
      layoutTransition={headerTransition}
      key="colorModeToggle"
      alignItems="center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      mb={[null, 'auto']}
      mr={isSubmitting ? null : 2}>
      <ColorModeToggle />
    </AnimatedFlex>
  );
  const layout = {
    false: {
      sm: [title, resetButton, colorModeToggle],
      md: [resetButton, title, colorModeToggle],
      lg: [resetButton, title, colorModeToggle],
      xl: [resetButton, title, colorModeToggle],
    },
    true: {
      sm: [resetButton, colorModeToggle, title],
      md: [resetButton, title, colorModeToggle],
      lg: [resetButton, title, colorModeToggle],
      xl: [resetButton, title, colorModeToggle],
    },
  };
  return (
    <Flex
      px={2}
      zIndex="4"
      as="header"
      width="full"
      flex="0 1 auto"
      bg={bg[colorMode]}
      color="gray.500"
      {...props}>
      <Flex
        w="100%"
        mx="auto"
        pt={6}
        justify="space-between"
        flex="1 0 auto"
        alignItems={isSubmitting ? 'center' : 'flex-start'}>
        {layout[isSubmitting][mediaSize]}
      </Flex>
    </Flex>
  );
};
