import type { MotionProps } from 'framer-motion';

declare global {
  type Dict<T = string> = Record<string, T>;
  type ValueOf<T> = T[keyof T];

  type TRPKIStates = 0 | 1 | 2 | 3;

  type TResponseLevel = 'success' | 'warning' | 'error' | 'danger';

  interface IRoute {
    prefix: string;
    active: boolean;
    age: number;
    weight: number;
    med: number;
    local_preference: number;
    as_path: number[];
    communities: string[];
    next_hop: string;
    source_as: number;
    source_rid: string;
    peer_rid: string;
    rpki_state: TRPKIStates;
  }

  type TRoute = {
    prefix: string;
    active: boolean;
    age: number;
    weight: number;
    med: number;
    local_preference: number;
    as_path: number[];
    communities: string[];
    next_hop: string;
    source_as: number;
    source_rid: string;
    peer_rid: string;
    rpki_state: TRPKIStates;
  };
  type TRouteField = { [k in keyof TRoute]: ValueOf<TRoute> };

  type TStructuredResponse = {
    vrf: string;
    count: number;
    routes: TRoute[];
    winning_weight: 'high' | 'low';
  };
  type TQueryResponse = {
    random: string;
    cached: boolean;
    runtime: number;
    level: TResponseLevel;
    timestamp: string;
    keywords: string[];
    output: string | TStructuredResponse;
    format: 'text/plain' | 'application/json';
  };
  type ReactRef<T = HTMLElement> = MutableRefObject<T>;

  type Animated<T> = Omit<T, keyof MotionProps> &
    Omit<MotionProps, keyof T> & { transition?: MotionProps['transition'] };

  type MeronexIcon = import('@meronex/icons').IconBaseProps;
}
