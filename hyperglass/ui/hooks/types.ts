export interface TOpposingOptions {
  light?: string;
  dark?: string;
}

export interface TStringTableData extends Omit<TQueryResponse, 'output'> {
  output: TStructuredResponse;
}

export type TUseGreetingReturn = [boolean, () => void];
