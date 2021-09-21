import type { Config } from '~/types';

export interface THyperglassProvider {
  config: Config;
  children: React.ReactNode;
}
