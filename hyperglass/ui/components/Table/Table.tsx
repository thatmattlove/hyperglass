import { Flex, Icon, Text } from '@chakra-ui/core';
import { usePagination, useSortBy, useTable } from 'react-table';
import { useMedia } from '~/context';
import { CardBody, CardFooter, CardHeader, If } from '~/components';
import { TableMain } from './TableMain';
import { TableCell } from './TableCell';
import { TableHead } from './TableHead';
import { TableRow } from './TableRow';
import { TableBody } from './TableBody';
import { TableIconButton } from './TableIconButton';
import { TableSelectShow } from './TableSelectShow';

import type { ITable } from './types';

export const Table = (props: ITable) => {
  const {
    columns,
    data,
    heading,
    onRowClick,
    striped = false,
    bordersVertical = false,
    bordersHorizontal = false,
    cellRender,
    rowHighlightProp,
    rowHighlightBg,
    rowHighlightColor,
  } = props;

  const { isSm, isMd } = useMedia();

  const defaultColumn = {
    minWidth: 100,
    width: 150,
    maxWidth: 300,
  };

  let hiddenColumns = [] as string[];

  for (const col of columns) {
    if (col.hidden) {
      hiddenColumns.push(col.accessor);
    }
  }

  const table = useTable(
    {
      columns,
      defaultColumn,
      data,
      initialState: { hiddenColumns },
    },
    useSortBy,
    usePagination,
  );

  const {
    getTableProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    pageOptions,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    state: { pageIndex, pageSize },
  } = table;

  return (
    <CardBody>
      {heading && <CardHeader>{heading}</CardHeader>}
      <TableMain {...getTableProps()}>
        <TableHead>
          {headerGroups.map((headerGroup, i) => (
            <TableRow index={i} {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <TableCell
                  as="th"
                  align={column.align}
                  {...column.getHeaderProps()}
                  {...column.getSortByToggleProps()}>
                  <Text fontSize="sm" fontWeight="bold" display="inline-block">
                    {column.render('Header')}
                  </Text>
                  <If condition={column.isSorted}>
                    <If condition={column.isSortedDesc}>
                      <Icon name="chevron-down" size={4} ml={1} />
                    </If>
                    <If condition={!column.isSortedDesc}>
                      <Icon name="chevron-up" size={4} ml={1} />
                    </If>
                  </If>
                  <If condition={!column.isSorted}>{''}</If>
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableHead>
        <TableBody>
          {page.map(
            (row, key) =>
              prepareRow(row) || (
                <TableRow
                  index={key}
                  doStripe={striped}
                  doHorizontalBorders={bordersHorizontal}
                  onClick={() => onRowClick && onRowClick(row)}
                  key={key}
                  highlight={row.values[rowHighlightProp ?? ''] ?? false}
                  highlightBg={rowHighlightBg}
                  highlightColor={rowHighlightColor}
                  {...row.getRowProps()}>
                  {row.cells.map((cell, i) => {
                    return (
                      <TableCell
                        align={cell.column.align}
                        cell={cell}
                        bordersVertical={[bordersVertical, i]}
                        key={cell.row.index}
                        {...cell.getCellProps()}>
                        {cell.render(cellRender ?? 'Cell')}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ),
          )}
        </TableBody>
      </TableMain>
      <CardFooter>
        <Flex direction="row">
          <TableIconButton
            mr={2}
            onClick={() => gotoPage(0)}
            isDisabled={!canPreviousPage}
            icon={() => <Icon name="arrow-left" size={3} />}
          />
          <TableIconButton
            mr={2}
            onClick={() => previousPage()}
            isDisabled={!canPreviousPage}
            icon={() => <Icon name="chevron-left" size={6} />}
          />
        </Flex>
        <Flex justifyContent="center" alignItems="center">
          <Text fontSize="sm" mr={4} whiteSpace="nowrap">
            Page{' '}
            <strong>
              {pageIndex + 1} of {pageOptions.length}
            </strong>{' '}
          </Text>
          {!(isSm || isMd) && (
            <TableSelectShow
              value={pageSize}
              onChange={e => {
                setPageSize(Number(e.target.value));
              }}
            />
          )}
        </Flex>
        <Flex direction="row">
          <TableIconButton
            ml={2}
            isDisabled={!canNextPage}
            onClick={() => nextPage()}
            icon={() => <Icon name="chevron-right" size={6} />}
          />
          <TableIconButton
            ml={2}
            onClick={() => gotoPage(pageCount ? pageCount - 1 : 1)}
            isDisabled={!canNextPage}
            icon={() => <Icon name="arrow-right" size={3} />}
          />
        </Flex>
      </CardFooter>
    </CardBody>
  );
};
