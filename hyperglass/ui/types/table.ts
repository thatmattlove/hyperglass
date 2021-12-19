import type { CellProps } from 'react-table';

export interface TableColumn {
  Header: string;
  accessor: keyof Route;
  align: string;
  hidden: boolean;
}

export type CellRenderProps = {
  column: CellProps<RouteField>['column'];
  row: CellProps<RouteField>['row'];
  value: CellProps<RouteField>['value'];
};
