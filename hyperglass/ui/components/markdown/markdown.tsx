import ReactMarkdown from 'react-markdown';
import {
  Br,
  List,
  Link,
  Table,
  Heading,
  Divider,
  ListItem,
  CodeBlock,
  TableData,
  Paragraph,
  InlineCode,
} from './elements';

import type { ReactMarkdownProps } from 'react-markdown';
import type { TMarkdown } from './types';

const renderers = {
  break: Br,
  link: Link,
  list: List,
  table: Table,
  code: CodeBlock,
  heading: Heading,
  listItem: ListItem,
  paragraph: Paragraph,
  tableCell: TableData,
  inlineCode: InlineCode,
  thematicBreak: Divider,
} as ReactMarkdownProps['renderers'];

export const Markdown: React.FC<TMarkdown> = (props: TMarkdown) => (
  <ReactMarkdown renderers={renderers} source={props.content} />
);
