/* eslint-disable */

import type {
  TableInstance,
  UseSortByHooks,
  UseSortByState,
  UseFiltersState,
  UseGroupByHooks,
  UseGroupByState,
  UseExpandedHooks,
  UseExpandedState,
  UseSortByOptions,
  UseFiltersOptions,
  UseGroupByOptions,
  UseRowSelectHooks,
  UseRowSelectState,
  UseExpandedOptions,
  UseGroupByRowProps,
  UsePaginationState,
  UseColumnOrderState,
  UseExpandedRowProps,
  UseGroupByCellProps,
  UseRowSelectOptions,
  UsePaginationOptions,
  UseRowSelectRowProps,
  UseSortByColumnProps,
  UseFiltersColumnProps,
  UseGlobalFiltersState,
  UseGroupByColumnProps,
  UseResizeColumnsState,
  UseSortByColumnOptions,
  UseSortByInstanceProps,
  UseFiltersColumnOptions,
  UseFiltersInstanceProps,
  UseGlobalFiltersOptions,
  UseGroupByColumnOptions,
  UseGroupByInstanceProps,
  UseResizeColumnsOptions,
  UseExpandedInstanceProps,
  UseRowSelectInstanceProps,
  UsePaginationInstanceProps,
  UseColumnOrderInstanceProps,
  UseResizeColumnsColumnProps,
  UseGlobalFiltersInstanceProps,
  UseResizeColumnsColumnOptions,
} from 'react-table';

declare module 'react-table' {
  export interface UseFlexLayoutInstanceProps<D extends object> {
    totalColumnsMinWidth: number;
  }

  export interface UseFlexLayoutColumnProps<D extends object> {
    totalMinWidth: number;
  }

  export interface TableOptions<D extends object>
    extends UseExpandedOptions<D>,
      UseFiltersOptions<D>,
      UseFiltersOptions<D>,
      UseGlobalFiltersOptions<D>,
      UseGroupByOptions<D>,
      UsePaginationOptions<D>,
      UseResizeColumnsOptions<D>,
      UseRowSelectOptions<D>,
      UseSortByOptions<D> {}

  export interface Hooks<D extends object = {}>
    extends UseExpandedHooks<D>,
      UseGroupByHooks<D>,
      UseRowSelectHooks<D>,
      UseSortByHooks<D> {}

  export interface TableInstance<D extends object = {}>
    extends UseColumnOrderInstanceProps<D>,
      UseExpandedInstanceProps<D>,
      UseFiltersInstanceProps<D>,
      UseGlobalFiltersInstanceProps<D>,
      UseGroupByInstanceProps<D>,
      UsePaginationInstanceProps<D>,
      UseRowSelectInstanceProps<D>,
      UseFlexLayoutInstanceProps<D>,
      UsePaginationInstanceProps<D>,
      UseSortByInstanceProps<D> {}

  export interface TableState<D extends object = {}>
    extends UseColumnOrderState<D>,
      UseExpandedState<D>,
      UseFiltersState<D>,
      UseGlobalFiltersState<D>,
      UseGroupByState<D>,
      UsePaginationState<D>,
      UseResizeColumnsState<D>,
      UseRowSelectState<D>,
      UseSortByState<D> {
    rowCount: number;
  }

  export interface ColumnInterface<D extends object = {}>
    extends UseFiltersColumnOptions<D>,
      UseGroupByColumnOptions<D>,
      UseResizeColumnsColumnOptions<D>,
      UseSortByColumnOptions<D> {
    align?: 'left' | 'right' | 'center';
  }

  export interface ColumnInstance<D extends object = {}>
    extends UseFiltersColumnProps<D>,
      UseGroupByColumnProps<D>,
      UseResizeColumnsColumnProps<D>,
      UseFlexLayoutColumnProps<D>,
      UseSortByColumnProps<D> {}

  export interface Cell<D extends object = {}> extends UseGroupByCellProps<D> {}

  export interface Row<D extends object = {}>
    extends UseExpandedRowProps<D>,
      UseGroupByRowProps<D>,
      UseRowSelectRowProps<D> {}
}

export type TableMouseEventHandler = (instance: TableInstance<T>) => React.MouseEventHandler;
