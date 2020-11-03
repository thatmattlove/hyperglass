interface IIf {
  condition: boolean;
  render?: (rest: any) => JSX.Element;
  [k: string]: any;
}
