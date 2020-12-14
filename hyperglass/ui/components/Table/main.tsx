import * as React from 'react';
import dynamic from 'next/dynamic';
import { Flex, Icon, Text } from '@chakra-ui/react';
import { usePagination, useSortBy, useTable } from 'react-table';
import { useMobile } from '~/context';
import { CardBody, CardFooter, CardHeader, If } from '~/components';
import { TableMain } from './table';
import { TableCell } from './cell';
import { TableHead } from './head';
import { TableRow } from './row';
import { TableBody } from './body';
import { TableIconButton } from './button';
import { TableSelectShow } from './pageSelect';

import type { TableOptions, PluginHook, Row } from 'react-table';
import type { TTable } from './types';

const ChevronUp = dynamic<MeronexIcon>(() => import('@meronex/icons/fa').then(i => i.FaChevronUp));

const ChevronDown = dynamic<MeronexIcon>(() =>
  import('@meronex/icons/fa').then(i => i.FaChevronDown),
);

const DoubleChevronRight = dynamic<MeronexIcon>(() =>
  import('@meronex/icons/fi').then(i => i.FiChevronsRight),
);
const DoubleChevronLeft = dynamic<MeronexIcon>(() =>
  import('@meronex/icons/fi').then(i => i.FiChevronsLeft),
);

export function Table(props: TTable) {
  const {
    data,
    columns,
    heading,
    cellRender,
    rowHighlightBg,
    striped = false,
    rowHighlightProp,
    bordersVertical = false,
    bordersHorizontal = false,
  } = props;

  const isMobile = useMobile();

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

  const options = {
    columns,
    defaultColumn,
    data,
    initialState: { hiddenColumns },
  } as TableOptions<TRoute>;

  const plugins = [useSortBy, usePagination] as PluginHook<TRoute>[];

  const instance = useTable<TRoute>(options, ...plugins);

  const {
    page,
    gotoPage,
    nextPage,
    pageCount,
    prepareRow,
    canNextPage,
    pageOptions,
    setPageSize,
    headerGroups,
    previousPage,
    getTableProps,
    canPreviousPage,
    state: { pageIndex, pageSize },
  } = instance;

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
                  <If c={column.isSorted}>
                    <If c={typeof column.isSortedDesc !== 'undefined'}>
                      <Icon as={ChevronDown} boxSize={4} ml={1} />
                    </If>
                    <If c={!column.isSortedDesc}>
                      <Icon as={ChevronUp} boxSize={4} ml={1} />
                    </If>
                  </If>
                  <If c={!column.isSorted}>{''}</If>
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableHead>
        <TableBody>
          {page.map((row, key) => {
            prepareRow(row);
            return (
              <TableRow
                index={key}
                doStripe={striped}
                highlightBg={rowHighlightBg}
                doHorizontalBorders={bordersHorizontal}
                highlight={row.values[rowHighlightProp ?? ''] ?? false}
                {...row.getRowProps()}>
                {row.cells.map((cell, i) => {
                  return (
                    <TableCell
                      align={cell.column.align}
                      bordersVertical={[bordersVertical, i]}
                      {...cell.getCellProps()}>
                      {/* {cellRender ?? cell.render('Cell')} */}
                      {React.createElement(cellRender, cell)}
                    </TableCell>
                  );
                })}
              </TableRow>
            );
          })}
        </TableBody>
      </TableMain>
      <CardFooter>
        <Flex direction="row">
          <TableIconButton
            mr={2}
            onClick={() => gotoPage(0)}
            isDisabled={!canPreviousPage}
            icon={<Icon as={DoubleChevronLeft} boxSize={3} />}
          />
          <TableIconButton
            mr={2}
            onClick={() => previousPage()}
            isDisabled={!canPreviousPage}
            icon={<Icon as={DoubleChevronLeft} boxSize={6} />}
          />
        </Flex>
        <Flex justifyContent="center" alignItems="center">
          <Text fontSize="sm" mr={4} whiteSpace="nowrap">
            Page{' '}
            <strong>
              {pageIndex + 1} of {pageOptions.length}
            </strong>{' '}
          </Text>
          {!isMobile && (
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
            onClick={nextPage}
            isDisabled={!canNextPage}
            icon={<Icon as={ChevronUp} boxSize={6} />}
          />
          <TableIconButton
            ml={2}
            isDisabled={!canNextPage}
            icon={<Icon as={DoubleChevronRight} boxSize={3} />}
            onClick={() => gotoPage(pageCount ? pageCount - 1 : 1)}
          />
        </Flex>
      </CardFooter>
    </CardBody>
  );
}
