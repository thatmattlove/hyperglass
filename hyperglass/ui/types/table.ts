import type { CellProps } from 'react-table';

export interface TColumn {
  Header: string;
  accessor: keyof TRoute;
  align: string;
  hidden: boolean;
}

export type TCellRender = {
  column: CellProps<TRouteField>['column'];
  row: CellProps<TRouteField>['row'];
  value: CellProps<TRouteField>['value'];
};
