import { Box, useColorMode } from '@chakra-ui/core';
import { useColorValue } from '~/context';
import { useOpposingColor } from '~/hooks';

import type { ITableRow } from './types';

export const TableRow = (props: ITableRow) => {
  const {
    highlight = false,
    highlightBg = 'primary',
    doStripe = false,
    doHorizontalBorders = false,
    index = 0,
    ...rest
  } = props;
  const { colorMode } = useColorMode();

  const alpha = useColorValue('100', '200');
  const alphaHover = useColorValue('200', '100');
  const bgStripe = useColorValue('blackAlpha.50', 'whiteAlpha.50');
  let hoverBg = useColorValue('blackAlpha.50', 'whiteAlpha.50');
  const rowBorder = useColorValue(
    { borderTop: '1px', borderTopColor: 'blackAlpha.100' },
    { borderTop: '1px', borderTopColor: 'whiteAlpha.100' },
  );
  let bg;
  const color = useOpposingColor(bgStripe);

  if (highlight) {
    bg = `${highlightBg}.${alpha}`;
    hoverBg = `${highlightBg}.${alphaHover}`;
  } else if (doStripe && index % 2 !== 0) {
    bg = bgStripe;
  }

  const borderProps = doHorizontalBorders && index !== 0 ? rowBorder : {};

  return (
    <Box
      as="tr"
      bg={bg}
      color={highlight ? color : undefined}
      fontWeight={highlight ? 'bold' : undefined}
      _hover={{
        cursor: 'pointer',
        backgroundColor: highlight ? `${highlightBg}.${alphaHover}` : hoverBg,
      }}
      {...borderProps}
      {...rest}
    />
  );
};
