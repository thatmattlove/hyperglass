import type { NodeProps } from 'react-flow-renderer';

export interface TChart {
  data: TStructuredResponse;
}

export interface TPath {
  device: string;
}

export interface TNode<D extends unknown> extends Omit<NodeProps, 'data'> {
  data: D;
}

export interface TNodeData {
  asn: string;
  name: string;
  hasChildren: boolean;
  hasParents?: boolean;
}

export interface BasePath {
  asn: string;
  name: string;
}

export interface TPathButton {
  onOpen(): void;
}
