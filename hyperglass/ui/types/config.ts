import type { Theme } from './theme';
import type { CamelCasedPropertiesDeep, CamelCasedProperties } from 'type-fest';

type Side = 'left' | 'right' | string;

export type ParsedDataField = [string, keyof Route, 'left' | 'right' | 'center' | null];

interface _Messages {
  no_input: string;
  feature_not_enabled: string;
  invalid_input: string;
  general: string;
  request_timeout: string;
  connection_error: string;
  authentication_error: string;
  no_output: string;
}

interface _ThemeConfig {
  colors: Record<string, string>;
  default_color_mode: 'light' | 'dark' | null;
  fonts: Theme.Fonts;
}

interface _Text {
  title_mode: string;
  title: string;
  subtitle: string;
  query_location: string;
  query_type: string;
  query_target: string;
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
  ip_error: string;
  no_ip: string;
  ip_select: string;
  ip_button: string;
}

interface _Greeting {
  enable: boolean;
  title: string;
  button: string;
  required: boolean;
}

interface _Logo {
  width: string;
  height: string | null;
  light_format: string;
  dark_format: string;
}

interface _Link {
  title: string;
  url: string;
  show_icon: boolean;
  side: Side;
  order: number;
}

interface _Menu {
  title: string;
  content: string;
  side: Side;
  order: number;
}

interface _Credit {
  enable: boolean;
}

interface _Highlight {
  pattern: string;
  label: string | null;
  color: string;
}

interface _Web {
  credit: _Credit;
  dns_provider: { name: string; url: string };
  links: _Link[];
  menus: _Menu[];
  greeting: _Greeting;
  logo: _Logo;
  text: _Text;
  theme: _ThemeConfig;
  location_display_mode: 'auto' | 'gallery' | 'dropdown' | string;
  highlight: _Highlight[];
}

type _DirectiveBase = {
  id: string;
  name: string;
  field_type: 'text' | 'select' | null | string;
  description: string;
  groups: string[];
  info: string | null;
};

type _DirectiveOption = {
  name: string;
  value: string;
  description: string | null;
};

type _DirectiveSelect = _DirectiveBase & {
  options: _DirectiveOption[];
};

type _Directive = _DirectiveBase | _DirectiveSelect;

interface _Device {
  id: string;
  name: string;
  group: string | null;
  avatar: string | null;
  directives: _Directive[];
  description: string | null;
}

interface _Content {
  credit: string;
  greeting: string;
}

interface _Cache {
  show_text: boolean;
  timeout: number;
}

type _Config = _ConfigDeep & _ConfigShallow;

interface _DeviceGroup {
  group: string | null;
  locations: _Device[];
}

interface _ConfigDeep {
  cache: _Cache;
  web: _Web;
  messages: _Messages;
  devices: _DeviceGroup[];
  content: _Content;
}

interface _ConfigShallow {
  developer_mode: boolean;
  primary_asn: string;
  request_timeout: number;
  org_name: string;
  site_title: string;
  site_description: string;
  version: string;
  parsed_data_fields: ParsedDataField[];
}

export interface Favicon {
  rel: string | null;
  dimensions: [number, number];
  image_format: string;
  prefix: string;
}

export type Config = CamelCasedPropertiesDeep<_ConfigDeep> & CamelCasedProperties<_ConfigShallow>;
export type ThemeConfig = CamelCasedProperties<_ThemeConfig>;
export type Content = CamelCasedProperties<_Content>;
export type Device = CamelCasedPropertiesDeep<_Device>;
export type DeviceGroup = CamelCasedPropertiesDeep<_DeviceGroup>;
export type Directive = CamelCasedPropertiesDeep<_Directive>;
export type DirectiveSelect = CamelCasedPropertiesDeep<_DirectiveSelect>;
export type DirectiveOption = CamelCasedPropertiesDeep<_DirectiveOption>;
export type Text = CamelCasedProperties<_Text>;
export type Web = CamelCasedPropertiesDeep<_Web>;
export type Greeting = CamelCasedProperties<_Greeting>;
export type Logo = CamelCasedProperties<_Logo>;
export type Link = CamelCasedProperties<_Link>;
export type Menu = CamelCasedProperties<_Menu>;
export type Highlight = CamelCasedProperties<_Highlight>;
