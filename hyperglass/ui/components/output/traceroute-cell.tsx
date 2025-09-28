import { MonoField, ASNField, LatencyField, LossField, HostnameField } from './traceroute-fields';

import type { TracerouteCellRenderProps } from '~/types';

interface TracerouteCellProps {
  data: TracerouteCellRenderProps;
  rawData: TracerouteResult;
}

export const TracerouteCell = (props: TracerouteCellProps): JSX.Element => {
  const { data, rawData } = props;
  const cellId = data.column.id as keyof TracerouteHop;
  
  // DEBUG: Log row values to see what's available
  console.log('TracerouteCell debug:', {
    cellId,
    value: data.value,
    rowValues: data.row?.values,
    rowOriginal: data.row?.original
  });
  
  // For IP address field, prefer display_ip if available (for truncated IPv6)
  const getIPValue = () => {
    if (cellId === 'ip_address') {
      const hop = data.row?.original as TracerouteHop | undefined;
      if (hop && hop.display_ip) {
        return hop.display_ip;
      }
      if (hop && hop.ip_address) {
        return hop.ip_address;
      }
    }
    return data.value;
  };
  
  const component = {
    hop_number: <MonoField v={data.value} />,
    ip_address: <MonoField v={getIPValue()} />,
    display_ip: <MonoField v={data.value} />, // For truncated IPv6 display
    hostname: <HostnameField hostname={data.value} />,
    loss_pct: <LossField loss={data.value} />,
    sent_count: <MonoField v={data.value} />,
    last_rtt: <LatencyField rtt={data.value} />,
    avg_rtt: <LatencyField rtt={data.value} />,
    best_rtt: <LatencyField rtt={data.value} />,
    worst_rtt: <LatencyField rtt={data.value} />,
    asn: <ASNField asn={data.value} org={data.row?.original?.org || data.row?.values?.org} />,
    org: null, // Hidden, displayed as part of ASN
    prefix: <MonoField v={data.value} />,
    country: <MonoField v={data.value} />,
    rir: <MonoField v={data.value} />,
    allocated: <MonoField v={data.value} />,
    rtt1: null, // Not displayed directly in table
    rtt2: null, // Not displayed directly in table
    rtt3: null, // Not displayed directly in table
  };
  
  return component[cellId] ?? <MonoField v={data.value} />;
};