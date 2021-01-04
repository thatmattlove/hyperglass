import type { TIf } from './types';

export const If: React.FC<TIf> = (props: TIf) => {
  const { c, children } = props;
  return c ? <>{children}</> : null;
};
