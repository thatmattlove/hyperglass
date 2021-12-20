import { chakra } from '@chakra-ui/react';
import { useColorValue } from '~/hooks';

import type { BoxProps } from '@chakra-ui/react';

interface TableCellProps extends Omit<BoxProps, 'align'> {
  bordersVertical?: [boolean, number];
  align?: 'left' | 'right' | 'center';
}

export const TableCell = (props: TableCellProps): JSX.Element => {
  const { bordersVertical = [false, 0], align, ...rest } = props;
  const [doVerticalBorders, index] = bordersVertical;
  const borderLeftColor = useColorValue('blackAlpha.100', 'whiteAlpha.100');

  let borderProps = {};
  if (doVerticalBorders && index !== 0) {
    borderProps = { borderLeft: '1px solid', borderLeftColor };
  }

  return (
    <chakra.td
      p={4}
      m={0}
      w="1%"
      textAlign={align}
      whiteSpace="nowrap"
      {...borderProps}
      {...rest}
    />
  );
};
