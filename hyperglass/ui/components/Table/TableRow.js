import * as React from 'react';
import { PseudoBox, useColorMode, useTheme } from '@chakra-ui/core';
import { opposingColor } from 'app/util';

const hoverBg = { dark: 'whiteAlpha.50', light: 'blackAlpha.50' };
const bgStripe = { dark: 'whiteAlpha.50', light: 'blackAlpha.50' };
const rowBorder = {
  dark: { borderTop: '1px', borderTopColor: 'whiteAlpha.100' },
  light: { borderTop: '1px', borderTopColor: 'blackAlpha.100' },
};
const alphaMap = { dark: '200', light: '100' };
const alphaMapHover = { dark: '100', light: '200' };

export const TableRow = ({
  highlight = false,
  highlightBg = 'primary',
  doStripe = false,
  doHorizontalBorders = false,
  index = 0,
  children = false,
  ...props
}) => {
  const { colorMode } = useColorMode();
  const theme = useTheme();

  let bg = null;
  if (highlight) {
    bg = `${highlightBg}.${alphaMap[colorMode]}`;
  } else if (doStripe && index % 2 !== 0) {
    bg = bgStripe[colorMode];
  }
  const color = highlight ? opposingColor(theme, bg) : null;

  const borderProps = doHorizontalBorders && index !== 0 ? rowBorder[colorMode] : {};
  return (
    <PseudoBox
      as="tr"
      _hover={{
        cursor: 'pointer',
        backgroundColor: highlight
          ? `${highlightBg}.${alphaMapHover[colorMode]}`
          : hoverBg[colorMode],
      }}
      bg={bg}
      color={color}
      fontWeight={highlight ? 'bold' : null}
      {...borderProps}
      {...props}>
      {children}
    </PseudoBox>
  );
};
