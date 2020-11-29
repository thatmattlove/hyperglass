export interface TColumn {
  Header: string;
  accessor: keyof TRoute;
  align: string;
  hidden: boolean;
}
