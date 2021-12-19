import { Flex } from '@chakra-ui/react';
import { Table } from '~/components';
import { useConfig } from '~/context';
import { Cell } from './cell';

import type { FlexProps } from '@chakra-ui/react';
import type { TableColumn, ParsedDataField, CellRenderProps } from '~/types';

type BGPTableProps = Swap<FlexProps, 'children', StructuredResponse>;

function makeColumns(fields: ParsedDataField[]): TableColumn[] {
  return fields.map(pair => {
    const [header, accessor, align] = pair;

    const columnConfig = {
      align,
      accessor,
      hidden: false,
      Header: header,
    } as TableColumn;

    if (align === null) {
      columnConfig.hidden = true;
    }

    return columnConfig;
  });
}

export const BGPTable = (props: BGPTableProps): JSX.Element => {
  const { children: data, ...rest } = props;
  const { parsedDataFields } = useConfig();
  const columns = makeColumns(parsedDataFields);

  return (
    <Flex my={8} justify="center" maxW="100%" w="100%" {...rest}>
      <Table
        columns={columns}
        bordersHorizontal
        data={data.routes}
        rowHighlightBg="green"
        rowHighlightProp="active"
        Cell={(d: CellRenderProps) => <Cell data={d} rawData={data} />}
      />
    </Flex>
  );
};
