import { Flex } from '@chakra-ui/react';
import { Table } from '~/components';
import { useConfig } from '~/context';
import { Cell } from './cell';

import type { TColumn, ParsedDataField, TCellRender } from '~/types';
import type { TBGPTable } from './types';

function makeColumns(fields: ParsedDataField[]): TColumn[] {
  return fields.map(pair => {
    const [header, accessor, align] = pair;

    const columnConfig = {
      align,
      accessor,
      hidden: false,
      Header: header,
    } as TColumn;

    if (align === null) {
      columnConfig.hidden = true;
    }

    return columnConfig;
  });
}

export const BGPTable = (props: TBGPTable): JSX.Element => {
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
        Cell={(d: TCellRender) => <Cell data={d} rawData={data} />}
      />
    </Flex>
  );
};
