/** @jsx jsx */
import { jsx } from '@emotion/core';
import { Box, css } from '@chakra-ui/core';

export const TableBody = ({ children, ...props }) => (
  <Box
    as="tbody"
    overflowY="scroll"
    css={css({
      '&::-webkit-scrollbar': { display: 'none' },
      '&': { msOverflowStyle: 'none' },
    })}
    overflowX="hidden"
    {...props}>
    {children}
  </Box>
);
