export type TQueryTypes = '' | TValidQueryTypes;
export type TValidQueryTypes = 'bgp_route' | 'bgp_community' | 'bgp_aspath' | 'ping' | 'traceroute';

export interface TFormData {
  query_location: string[];
  query_type: TQueryTypes;
  query_vrf: string;
  query_target: string;
}

export interface TFormState {
  queryLocation: string[];
  queryType: TQueryTypes;
  queryVrf: string;
  queryTarget: string;
}

export interface TFormQuery extends Omit<TFormState, 'queryLocation'> {
  queryLocation: string;
}

export interface TStringTableData extends Omit<TQueryResponse, 'output'> {
  output: TStructuredResponse;
}

export interface TQueryResponseString extends Omit<TQueryResponse, 'output'> {
  output: string;
}
