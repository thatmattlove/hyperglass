import { Flex } from '@chakra-ui/react';
import { useConfig } from '~/context';
import { Table } from '~/components';
import { Cell } from './cell';

import type { TColumn, TParsedDataField, TCellRender } from '~/types';
import type { TBGPTable } from './types';

function makeColumns(fields: TParsedDataField[]): TColumn[] {
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

export const BGPTable: React.FC<TBGPTable> = (props: TBGPTable) => {
  const { children: data, ...rest } = props;
  const { parsed_data_fields } = useConfig();
  const columns = makeColumns(parsed_data_fields);

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
