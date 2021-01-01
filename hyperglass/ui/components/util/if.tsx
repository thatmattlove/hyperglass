import type { TIf } from './types';

export const If = (props: TIf) => {
  const { c, render, children, ...rest } = props;
  return c ? (render ? render(rest) : children) : null;
};
