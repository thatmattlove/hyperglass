import * as React from 'react';
import { Button, Flex } from '@chakra-ui/core';
import { motion } from 'framer-motion';

const AnimatedFlex = motion.custom(Flex);

export const FooterButton = React.forwardRef(({ onClick, side, children, ...props }, ref) => {
  return (
    <AnimatedFlex
      p={0}
      w="auto"
      ref={ref}
      flexGrow={0}
      float={side}
      flexShrink={0}
      maxWidth="100%"
      flexBasis="auto"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}>
      <Button size="xs" variant="ghost" onClick={onClick} {...props}>
        {children}
      </Button>
    </AnimatedFlex>
  );
});
