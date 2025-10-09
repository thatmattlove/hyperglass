import { Flex } from '@chakra-ui/react';
import { Table } from '~/components';
import { TracerouteCell } from './traceroute-cell';

import type { FlexProps } from '@chakra-ui/react';
import type { TracerouteTableColumn, TracerouteCellRenderProps } from '~/types';

type TracerouteTableProps = Swap<FlexProps, 'children', TracerouteResult>;

// Column definition for the traceroute table using BGP table structure
// Format: "Hop | IP | HostName (reverse dns) | ASN | Loss | Sent | Last | AVG | BEST | Worst"
const tracerouteColumns: TracerouteTableColumn[] = [
  { Header: 'Hop', accessor: 'hop_number', align: 'center', hidden: false },
  { Header: 'IP Address', accessor: 'ip_address', align: 'left', hidden: false },
  { Header: 'Hostname', accessor: 'hostname', align: 'left', hidden: false },
  { Header: 'ASN', accessor: 'asn', align: 'center', hidden: false },
  { Header: 'Loss', accessor: 'loss_pct', align: 'center', hidden: false },
  { Header: 'Sent', accessor: 'sent_count', align: 'center', hidden: false },
  { Header: 'Last', accessor: 'last_rtt', align: 'right', hidden: false },
  { Header: 'AVG', accessor: 'avg_rtt', align: 'right', hidden: false },
  { Header: 'Best', accessor: 'best_rtt', align: 'right', hidden: false },
  { Header: 'Worst', accessor: 'worst_rtt', align: 'right', hidden: false },
];

export const TracerouteTable = (props: TracerouteTableProps): JSX.Element => {
  const { children: data, ...rest } = props;

  return (
    <Flex my={8} justify="center" maxW="100%" w="100%" {...rest}>
      <Table<TracerouteHop>
        columns={tracerouteColumns as any}
        bordersHorizontal
        data={data.hops}
        Cell={(d: TracerouteCellRenderProps) => <TracerouteCell data={d} rawData={data} />}
      />
    </Flex>
  );
};