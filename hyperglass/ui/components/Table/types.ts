import type { BoxProps, IconButtonProps } from '@chakra-ui/react';

import type { Theme, TColumn, TCellRender } from '~/types';

export interface TTable {
  data: TRoute[];
  striped?: boolean;
  columns: TColumn[];
  heading?: React.ReactNode;
  bordersVertical?: boolean;
  bordersHorizontal?: boolean;
  Cell?: React.FC<TCellRender>;
  rowHighlightProp?: keyof IRoute;
  rowHighlightBg?: Theme.ColorNames;
}

export interface TTableCell extends Omit<BoxProps, 'align'> {
  bordersVertical?: [boolean, number];
  align?: 'left' | 'right' | 'center';
}

export interface TTableRow extends BoxProps {
  highlightBg?: Theme.ColorNames;
  doHorizontalBorders?: boolean;
  highlight?: boolean;
  doStripe?: boolean;
  index: number;
}

export type TTableIconButton = Omit<IconButtonProps, 'aria-label'>;
