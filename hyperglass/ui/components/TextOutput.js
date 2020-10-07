/** @jsx jsx */
import { jsx } from '@emotion/core';
import { Box, css, useColorMode } from '@chakra-ui/core';

const bg = { dark: 'gray.800', light: 'blackAlpha.100' };
const color = { dark: 'white', light: 'black' };
const selectionBg = { dark: 'white', light: 'black' };
const selectionColor = { dark: 'black', light: 'white' };

export const TextOutput = ({ children, ...props }) => {
  const { colorMode } = useColorMode();

  return (
    <Box
      fontFamily="mono"
      mt={5}
      mx={2}
      p={3}
      border="1px"
      borderColor="inherit"
      rounded="md"
      bg={bg[colorMode]}
      color={color[colorMode]}
      fontSize="sm"
      whiteSpace="pre-wrap"
      as="pre"
      css={css({
        '&::selection': {
          backgroundColor: selectionBg[colorMode],
          color: selectionColor[colorMode],
        },
      })}
      {...props}>
      {children
        .split('\\n')
        .join('\n')
        .replace(/\n\n/g, '\n')}
    </Box>
  );
};
