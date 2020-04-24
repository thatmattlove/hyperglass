import * as React from "react";
import { useMemo } from "react";
import { Flex, Icon, Text } from "@chakra-ui/core";
import useMedia from "~/components/MediaProvider";
import { usePagination, useSortBy, useTable } from "react-table";
import Card from "~/components/Card";
import BottomSection from "~/components/Card/CardFooter";
import TopSection from "~/components/Card/CardHeader";
import MainTable from "./MainTable";
import TableCell from "./TableCell";
import TableHead from "./TableHead";
import TableRow from "./TableRow";
import TableBody from "./TableBody";
import TableIconButton from "./TableIconButton";
import TableSelectShow from "./TableSelectShow";

const Table = ({
  columns,
  data,
  tableHeading,
  initialPageSize = 10,
  onRowClick,
  striped = false,
  bordersVertical = false,
  bordersHorizontal = false,
  cellRender = null,
  rowHighlightProp,
  rowHighlightBg,
  rowHighlightColor
}) => {
  const tableColumns = useMemo(() => columns, [columns]);

  const { isSm, isMd } = useMedia();

  const isTabletOrMobile = isSm ? true : isMd ? true : false;

  const defaultColumn = useMemo(
    () => ({
      minWidth: 100,
      width: 150,
      maxWidth: 300
    }),
    []
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
    state: { pageIndex, pageSize }
  } = useTable(
    {
      columns: tableColumns,
      defaultColumn,
      data,
      initialState: { pageIndex: 0, pageSize: initialPageSize }
    },
    useSortBy,
    usePagination
  );

  return (
    <Card>
      {!!tableHeading && <TopSection>{tableHeading}</TopSection>}
      <MainTable {...getTableProps()}>
        <TableHead>
          {headerGroups.map(headerGroup => (
            <TableRow
              key={headerGroup.id}
              {...headerGroup.getHeaderGroupProps()}
            >
              {headerGroup.headers.map(column => (
                <TableCell
                  as="th"
                  align={column.align}
                  key={column.id}
                  {...column.getHeaderProps()}
                  {...column.getSortByToggleProps()}
                >
                  <Text fontSize="sm" fontWeight="bold" display="inline-block">
                    {column.render("Header")}
                  </Text>
                  {column.isSorted ? (
                    column.isSortedDesc ? (
                      <Icon name="chevron-down" size={4} ml={1} />
                    ) : (
                      <Icon name="chevron-up" size={4} ml={1} />
                    )
                  ) : (
                    ""
                  )}
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
                  highlight={row.values[rowHighlightProp] ?? false}
                  highlightBg={rowHighlightBg}
                  highlightColor={rowHighlightColor}
                  {...row.getRowProps()}
                >
                  {row.cells.map((cell, i) => {
                    return (
                      <TableCell
                        align={cell.column.align}
                        cell={cell}
                        bordersVertical={[bordersVertical, i]}
                        key={cell.row.index}
                        {...cell.getCellProps()}
                      >
                        {cell.render(cellRender ?? "Cell")}
                      </TableCell>
                    );
                  })}
                </TableRow>
              )
          )}
        </TableBody>
      </MainTable>
      <BottomSection>
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
          <Text mr={4} whiteSpace="nowrap">
            Page{" "}
            <strong>
              {pageIndex + 1} of {pageOptions.length}
            </strong>{" "}
          </Text>
          {!isTabletOrMobile && (
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
      </BottomSection>
    </Card>
  );
};

Table.displayName = "Table";

export default Table;
