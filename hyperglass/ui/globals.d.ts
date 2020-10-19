import type { MotionProps } from 'framer-motion';

type Dict<T = string> = Record<string, T>;

type ReactRef<T = HTMLElement> = MutableRefObject<T>;

type Animated<T> = Omit<T, keyof MotionProps> &
  Omit<MotionProps, keyof T> & { transition?: MotionProps['transition'] };
