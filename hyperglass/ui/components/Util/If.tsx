export const If = (props: IIf) => {
  const { condition, render, children, ...rest } = props;
  return condition ? (render ? render(rest) : children) : null;
};
