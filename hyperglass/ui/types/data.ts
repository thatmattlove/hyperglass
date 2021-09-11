export type TQueryTypes = '' | TValidQueryTypes;
export type TValidQueryTypes = 'bgp_route' | 'bgp_community' | 'bgp_aspath' | 'ping' | 'traceroute';

export interface FormData {
  queryLocation: string[];
  queryType: string;
  queryTarget: string;
  queryGroup: string;
}

export interface TFormQuery extends Omit<FormData, 'queryLocation'> {
  queryLocation: string;
}

export interface TStringTableData extends Omit<QueryResponse, 'output'> {
  output: StructuredResponse;
}

export interface TQueryResponseString extends Omit<QueryResponse, 'output'> {
  output: string;
}
