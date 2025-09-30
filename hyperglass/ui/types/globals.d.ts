export declare global {
  type Dict<T = string> = Record<string, T>;

  type ValueOf<T> = T[keyof T];

  type Nullable<T> = T | null;

  type Get<T, K extends keyof T> = T[K];

  type Swap<T, K extends keyof T, V> = Record<K, V> & Omit<T, K>;

  type ArrayElement<ArrayType extends readonly unknown[]> =
    ArrayType extends readonly (infer ElementType)[] ? ElementType : never;

  type RPKIState = 0 | 1 | 2 | 3;

  type ResponseLevel = 'success' | 'warning' | 'error' | 'danger';

  type Route = {
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
    rpki_state: RPKIState;
  };

  type TracerouteHop = {
    hop_number: number;
    ip_address: string | null;
    display_ip: string | null;
    hostname: string | null;
    rtt1: number | null;
    rtt2: number | null;
    rtt3: number | null;
    loss_pct: number | null;
    sent_count: number | null;
    last_rtt: number | null;
    avg_rtt: number | null;
    best_rtt: number | null;
    worst_rtt: number | null;
    asn: string | null;
    org: string | null;
    prefix: string | null;
    country: string | null;
    rir: string | null;
    allocated: string | null;
  };

  type TracerouteResult = {
    target: string;
    source: string;
    hops: TracerouteHop[];
    max_hops: number;
    packet_size: number;
    raw_output: string | null;
  };

  type RouteField = { [K in keyof Route]: Route[K] };
  
  type TracerouteHopField = { [K in keyof TracerouteHop]: TracerouteHop[K] };

  type StructuredResponse = {
    vrf: string;
    count: number;
    routes: Route[];
    winning_weight: 'high' | 'low';
  };

  type TracerouteStructuredOutput = {
    vrf: string;
    target: string;
    source: string;
    hops: TracerouteHop[];
    max_hops: number;
    packet_size: number;
    raw_output: string | null;
  };

  type BGPStructuredOutput = StructuredResponse;

  type AllStructuredResponses = BGPStructuredOutput | TracerouteStructuredOutput;

  type QueryResponse = {
    random: string;
    cached: boolean;
    runtime: number;
    level: ResponseLevel;
    timestamp: string;
    keywords: string[];
    output: string | StructuredResponse;
    format: 'text/plain' | 'application/json';
  };

  type RequiredProps<T> = { [P in keyof T]-?: Exclude<T[P], undefined> };

  declare namespace NodeJS {
    export interface ProcessEnv {
      hyperglass: { favicons: import('./config').Favicon[]; version: string };
      buildId: string;
      UI_PARAMS: import('./config').Config;
    }
  }
}

declare module 'hyperglass.json' {
  type Config = import('./config').Config;
  export default Config;
}

declare module 'react' {
  // Enable generic typing with forwardRef.
  // eslint-disable-next-line @typescript-eslint/ban-types
  function forwardRef<T, P = {}>(
    render: (props: P, ref: React.Ref<T>) => React.ReactElement | null,
  ): (props: P & React.RefAttributes<T>) => React.ReactElement | null;
}
