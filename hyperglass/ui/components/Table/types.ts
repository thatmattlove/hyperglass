import type { BoxProps, IconButtonProps } from '@chakra-ui/react';

import type { Colors, TColumn } from '~/types';

export interface TTable {
  columns: TColumn[];
  data: TRoute[];
  heading?: React.ReactNode;
  striped?: boolean;
  bordersVertical?: boolean;
  bordersHorizontal?: boolean;
  cellRender?: React.ReactNode;
  rowHighlightProp?: keyof IRoute;
  rowHighlightBg?: keyof Colors;
}

export interface TTableCell extends Omit<BoxProps, 'align'> {
  bordersVertical?: [boolean, number];
  align?: 'left' | 'right' | 'center';
}

export interface TTableRow extends BoxProps {
  highlight?: boolean;
  highlightBg?: keyof Colors;
  doStripe?: boolean;
  doHorizontalBorders?: boolean;
  index: number;
}

export type TTableIconButton = Omit<IconButtonProps, 'aria-label'>;
