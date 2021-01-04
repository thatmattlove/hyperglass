import type { TIf } from './types';

export const If = (props: React.PropsWithChildren<TIf>): React.ReactNode | null => {
  const { c, children } = props;
  return c ? children : null;
};
