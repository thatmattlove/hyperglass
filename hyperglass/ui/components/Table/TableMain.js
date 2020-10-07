/** @jsx jsx */
import { jsx } from '@emotion/core';
import { Box, css, useTheme, useColorMode } from '@chakra-ui/core';

const scrollbar = { dark: 'whiteAlpha.300', light: 'blackAlpha.300' };
const scrollbarHover = { dark: 'whiteAlpha.400', light: 'blackAlpha.400' };
const scrollbarBg = { dark: 'whiteAlpha.50', light: 'blackAlpha.50' };

export const TableMain = ({ children, ...props }) => {
  const theme = useTheme();
  const { colorMode } = useColorMode();
  return (
    <Box
      as="table"
      display="block"
      css={css({
        '&::-webkit-scrollbar': { height: '5px' },
        '&::-webkit-scrollbar-track': {
          backgroundColor: scrollbarBg[colorMode],
        },
        '&::-webkit-scrollbar-thumb': {
          backgroundColor: scrollbar[colorMode],
        },
        '&::-webkit-scrollbar-thumb:hover': {
          backgroundColor: scrollbarHover[colorMode],
        },

        '-ms-overflow-style': { display: 'none' },
      })(theme)}
      overflowX="auto"
      borderRadius="md"
      boxSizing="border-box"
      {...props}>
      {children}
    </Box>
  );
};
