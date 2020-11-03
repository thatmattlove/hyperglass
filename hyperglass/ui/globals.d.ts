import type { MotionProps } from 'framer-motion';

declare global {
  import * as React from 'react';

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
    rpki_state: 0 | 1 | 2 | 3;
  }
  type ReactRef<T = HTMLElement> = MutableRefObject<T>;

  type Dict<T = string> = Record<string, T>;

  type Animated<T> = Omit<T, keyof MotionProps> &
    Omit<MotionProps, keyof T> & { transition?: MotionProps['transition'] };
  type ReactNode = React.ReactNode;
  type ReactFC = React.FunctionComponent;
}
