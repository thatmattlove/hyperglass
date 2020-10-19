import * as React from 'react';
import { forwardRef } from 'react';
import { Box, Collapse } from '@chakra-ui/core';
import { Markdown } from '~/components';

import type { IFooterContent } from './types';

export const FooterContent = (props: IFooterContent) => {
  const { isOpen = false, content, side = 'left', children: _, ...rest } = props;
  return (
    <Collapse
      px={6}
      py={4}
      w="auto"
      borderBottom="1px"
      display="flex"
      maxWidth="100%"
      isOpen={isOpen}
      flexBasis="auto"
      justifyContent={side === 'left' ? 'flex-start' : 'flex-end'}
      {...rest}>
      <Box textAlign={side}>
        <Markdown content={content} />
      </Box>
    </Collapse>
  );
};
