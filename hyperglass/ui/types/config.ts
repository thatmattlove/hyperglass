import { Colors, Fonts } from './theme';

export type TQueryFields = 'query_type' | 'query_target' | 'query_location' | 'query_vrf';

export interface IConfigMessages {
  no_input: string;
  acl_denied: string;
  acl_not_allowed: string;
  feature_not_enabled: string;
  invalid_input: string;
  invalid_field: string;
  general: string;
  request_timeout: string;
  connection_error: string;
  authentication_error: string;
  no_response: string;
  vrf_not_associated: string;
  vrf_not_found: string;
  no_output: string;
  parsing_error: string;
}

export interface IConfigTheme {
  colors: Colors;
  default_color_mode: 'light' | 'dark' | null;
  fonts: Fonts;
}

export interface IConfigWebText {
  title_mode: string;
  title: string;
  subtitle: string;
  query_location: string;
  query_type: string;
  query_target: string;
  query_vrf: string;
  fqdn_tooltip: string;
  cache_prefix: string;
  cache_icon: string;
  complete_time: string;
  rpki_invalid: string;
  rpki_valid: string;
  rpki_unknown: string;
  rpki_unverified: string;
}

export interface TConfigGreeting {
  enable: boolean;
  title: string;
  button: string;
  required: boolean;
}

export interface TConfigWebLogo {
  width: string;
  height: string | null;
  light_format: string;
  dark_format: string;
}

export interface IConfigWeb {
  credit: { enable: boolean };
  dns_provider: { name: string; url: string };
  external_link: { enable: boolean; title: string; url: string };
  greeting: TConfigGreeting;
  help_menu: { enable: boolean; title: string };
  logo: TConfigWebLogo;
  terms: { enable: boolean; title: string };
  text: IConfigWebText;
  theme: IConfigTheme;
}

export interface IQuery {
  name: string;
  enable: boolean;
  display_name: string;
}

export interface IBGPCommunity {
  community: string;
  display_name: string;
  description: string;
}

export interface IQueryBGPRoute extends IQuery {}
export interface IQueryBGPASPath extends IQuery {}
export interface IQueryPing extends IQuery {}
export interface IQueryTraceroute extends IQuery {}
export interface IQueryBGPCommunity extends IQuery {
  mode: 'input' | 'select';
  communities: IBGPCommunity[];
}

export interface IConfigQueries {
  bgp_route: IQueryBGPRoute;
  bgp_community: IQueryBGPCommunity;
  bgp_aspath: IQueryBGPASPath;
  ping: IQueryPing;
  traceroute: IQueryTraceroute;
  list: IQuery[];
}

interface IDeviceVrfBase {
  id: string;
  display_name: string;
}

export interface IDeviceVrf extends IDeviceVrfBase {
  ipv4: boolean;
  ipv6: boolean;
}

interface TDeviceBase {
  name: string;
  network: string;
  display_name: string;
}

export interface TDevice extends TDeviceBase {
  vrfs: IDeviceVrf[];
}

export interface TNetworkLocation extends TDeviceBase {
  vrfs: IDeviceVrfBase[];
}

export interface TNetwork {
  display_name: string;
  locations: TNetworkLocation[];
}

export type TParsedDataField = [string, keyof TRoute, 'left' | 'right' | 'center' | null];

export interface TQueryContent {
  content: string;
  enable: boolean;
  params: {
    primary_asn: IConfig['primary_asn'];
    org_name: IConfig['org_name'];
    site_title: IConfig['site_title'];
    title: string;
    [k: string]: string;
  };
}

export interface IConfigContent {
  help_menu: string;
  terms: string;
  credit: string;
  greeting: string;
  vrf: {
    [k: string]: {
      bgp_route: TQueryContent;
      bgp_community: TQueryContent;
      bgp_aspath: TQueryContent;
      ping: TQueryContent;
      traceroute: TQueryContent;
    };
  };
}

export interface IConfig {
  cache: { show_text: boolean; timeout: number };
  debug: boolean;
  developer_mode: boolean;
  primary_asn: string;
  request_timeout: number;
  org_name: string;
  google_analytics?: string;
  site_title: string;
  site_keywords: string[];
  site_description: string;
  web: IConfigWeb;
  messages: IConfigMessages;
  hyperglass_version: string;
  queries: IConfigQueries;
  devices: TDevice[];
  networks: TNetwork[];
  vrfs: IDeviceVrfBase[];
  parsed_data_fields: TParsedDataField[];
  content: IConfigContent;
}
