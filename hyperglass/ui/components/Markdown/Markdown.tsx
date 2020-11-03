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
} from './MDComponents';

import type { IMarkdown } from './types';

const mdComponents = {
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
};

export const Markdown = (props: IMarkdown) => (
  <ReactMarkdown renderers={mdComponents} source={props.content} />
);
