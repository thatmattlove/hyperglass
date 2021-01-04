import { Box } from '@chakra-ui/react';
import { useColorValue } from '~/context';
import { useOpposingColor } from '~/hooks';

import type { TTableRow } from './types';

export const TableRow: React.FC<TTableRow> = (props: TTableRow) => {
  const {
    index = 0,
    doStripe = false,
    highlight = false,
    highlightBg = 'primary',
    doHorizontalBorders = false,
    ...rest
  } = props;

  const alpha = useColorValue('100', '200');
  const alphaHover = useColorValue('200', '100');
  const bgStripe = useColorValue('blackAlpha.50', 'whiteAlpha.50');
  let hoverBg = useColorValue('blackAlpha.50', 'whiteAlpha.50');
  const rowBorder = useColorValue(
    { borderTop: '1px', borderTopColor: 'blackAlpha.100' },
    { borderTop: '1px', borderTopColor: 'whiteAlpha.100' },
  );
  let bg;

  if (highlight) {
    bg = `${String(highlightBg)}.${alpha}`;
    hoverBg = `${String(highlightBg)}.${alphaHover}`;
  } else if (doStripe && index % 2 !== 0) {
    bg = bgStripe;
  }
  const defaultBg = useColorValue('white', 'black');
  const color = useOpposingColor(bg ?? defaultBg);
  const borderProps = doHorizontalBorders && index !== 0 ? rowBorder : {};

  return (
    <Box
      as="tr"
      bg={bg}
      css={{ '& > td': { color } }}
      fontWeight={highlight ? 'bold' : undefined}
      _hover={{
        cursor: 'pointer',
        backgroundColor: highlight ? `${String(highlightBg)}.${alphaHover}` : hoverBg,
      }}
      {...borderProps}
      {...rest}
    />
  );
};
