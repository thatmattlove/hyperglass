import type { BoxProps } from '@chakra-ui/core';
import type { Colors } from '~/types';

export interface IColumn {
  Header: string;
  accessor: string;
  align: 'left' | 'right' | null;
  hidden: boolean;
}

export interface ITable {
  columns: IColumn[];
  data: IRoute[];
  heading?: ReactNode;
  onRowClick?: (row: IRoute) => void;
  striped?: boolean;
  bordersVertical?: boolean;
  bordersHorizontal?: boolean;
  cellRender?: ReactFC;
  rowHighlightProp?: keyof IRoute;
  rowHighlightBg?: keyof Colors;
  rowHighlightColor?: string;
}

export interface ITableCell extends BoxProps {
  bordersVertical: [boolean, number, number];
  align: BoxProps['textAlign'];
}

export interface ITableRow extends BoxProps {
  highlight?: boolean;
  highlightBg?: keyof Colors;
  doStripe?: boolean;
  doHorizontalBorders?: boolean;
  index: number;
}
