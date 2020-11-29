export interface TIf {
  c: boolean;
  render?: (rest: any) => JSX.Element;
  [k: string]: any;
}
