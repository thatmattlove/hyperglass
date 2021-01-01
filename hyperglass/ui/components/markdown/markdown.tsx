import ReactMarkdown from 'react-markdown';
import {
  List,
  ListItem,
  Heading,
  Link,
  CodeBlock,
  TableData,
  Paragraph,
  InlineCode,
  Divider,
  Table,
} from './elements';

import type { ReactMarkdownProps } from 'react-markdown';
import type { TMarkdown } from './types';

const renderers = {
  paragraph: Paragraph,
  link: Link,
  heading: Heading,
  inlineCode: InlineCode,
  list: List,
  listItem: ListItem,
  thematicBreak: Divider,
  code: CodeBlock,
  table: Table,
  tableCell: TableData,
} as ReactMarkdownProps['renderers'];

export const Markdown = (props: TMarkdown) => (
  <ReactMarkdown renderers={renderers} source={props.content} />
);
