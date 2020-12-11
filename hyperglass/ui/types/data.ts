export type TQueryTypes = '' | 'bgp_route' | 'bgp_community' | 'bgp_aspath' | 'ping' | 'traceroute';

export interface TFormData {
  query_location: string[];
  query_type: TQueryTypes;
  query_vrf: string;
  query_target: string;
}
