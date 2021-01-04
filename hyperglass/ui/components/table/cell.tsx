import { Box } from '@chakra-ui/react';
import { useColorValue } from '~/context';

import type { TTableCell } from './types';

export const TableCell: React.FC<TTableCell> = (props: TTableCell) => {
  const { bordersVertical = [false, 0], align, ...rest } = props;
  const [doVerticalBorders, index] = bordersVertical;
  const borderLeftColor = useColorValue('blackAlpha.100', 'whiteAlpha.100');

  let borderProps = {};
  if (doVerticalBorders && index !== 0) {
    borderProps = { borderLeft: '1px solid', borderLeftColor };
  }

  return (
    <Box
      p={4}
      m={0}
      w="1%"
      as="td"
      textAlign={align}
      whiteSpace="nowrap"
      {...borderProps}
      {...rest}
    />
  );
};
