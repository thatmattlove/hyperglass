import type { CellProps } from 'react-table';

export interface TColumn {
  Header: string;
  accessor: keyof Route;
  align: string;
  hidden: boolean;
}

export type TCellRender = {
  column: CellProps<RouteField>['column'];
  row: CellProps<RouteField>['row'];
  value: CellProps<RouteField>['value'];
};
