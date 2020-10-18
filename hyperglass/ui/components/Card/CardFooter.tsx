import * as React from 'react';
import { Flex } from '@chakra-ui/core';

import type { FlexProps } from '@chakra-ui/core';

export const CardFooter = (props: FlexProps) => (
  <Flex
    p={4}
    direction="column"
    overflowX="hidden"
    overflowY="hidden"
    flexDirection="row"
    borderTopWidth="1px"
    roundedBottomLeft={4}
    roundedBottomRight={4}
    justifyContent="space-between"
    {...props}
  />
);
