import { Flex } from '@chakra-ui/react';

import type { ICardFooter } from './types';

export const CardFooter = (props: ICardFooter) => (
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
