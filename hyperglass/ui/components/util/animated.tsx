/* eslint react/display-name: off */
import { Box, forwardRef } from '@chakra-ui/react';
import { motion, isValidMotionProp } from 'framer-motion';

import type { BoxProps } from '@chakra-ui/react';

/**
 * Combined Chakra + Framer Motion component.
 * @see https://chakra-ui.com/guides/integrations/with-framer
 */
export const AnimatedDiv = motion.custom(
  forwardRef<BoxProps, React.ElementType<BoxProps>>((props, ref) => {
    const chakraProps = Object.fromEntries(
      Object.entries(props).filter(([key]) => !isValidMotionProp(key)),
    );
    return <Box ref={ref} {...chakraProps} />;
  }),
);
