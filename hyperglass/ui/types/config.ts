import type { Theme } from './theme';

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
  colors: { [k: string]: string };
  default_color_mode: 'light' | 'dark' | null;
  fonts: Theme.Fonts;
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
  fqdn_message: string;
  fqdn_error: string;
  fqdn_error_button: string;
  cache_prefix: string;
  cache_icon: string;
  complete_time: string;
  rpki_invalid: string;
  rpki_valid: string;
  rpki_unknown: string;
  rpki_unverified: string;
  no_communities: string;
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

export interface TQuery {
  name: string;
  enable: boolean;
  display_name: string;
}

export interface TBGPCommunity {
  community: string;
  display_name: string;
  description: string;
}

export interface IQueryBGPRoute extends TQuery {}
export interface IQueryBGPASPath extends TQuery {}
export interface IQueryPing extends TQuery {}
export interface IQueryTraceroute extends TQuery {}
export interface IQueryBGPCommunity extends TQuery {
  mode: 'input' | 'select';
  communities: TBGPCommunity[];
}

export interface TConfigQueries {
  bgp_route: IQueryBGPRoute;
  bgp_community: IQueryBGPCommunity;
  bgp_aspath: IQueryBGPASPath;
  ping: IQueryPing;
  traceroute: IQueryTraceroute;
  list: TQuery[];
}

interface TDeviceVrfBase {
  id: string;
  display_name: string;
}

export interface TDeviceVrf extends TDeviceVrfBase {
  ipv4: boolean;
  ipv6: boolean;
}

interface TDeviceBase {
  _id: string;
  name: string;
  network: string;
}

export interface TDevice extends TDeviceBase {
  vrfs: TDeviceVrf[];
}

export interface TNetworkLocation extends TDeviceBase {
  vrfs: TDeviceVrf[];
}

export interface TNetwork {
  display_name: string;
  locations: TDevice[];
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
  google_analytics: string | null;
  site_title: string;
  site_keywords: string[];
  site_description: string;
  web: IConfigWeb;
  messages: IConfigMessages;
  hyperglass_version: string;
  queries: TConfigQueries;
  devices: TDevice[];
  networks: TNetwork[];
  vrfs: TDeviceVrfBase[];
  parsed_data_fields: TParsedDataField[];
  content: IConfigContent;
}

export interface Favicon {
  rel: string | null;
  dimensions: [number, number];
  image_format: string;
  prefix: string;
}

export interface FaviconComponent {
  rel: string;
  href: string;
  type: string;
}
