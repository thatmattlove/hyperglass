import ReactMarkdown from 'react-markdown';
import gfm from 'remark-gfm';
import {
  Br,
  List,
  Link,
  Table,
  Heading,
  Divider,
  ListItem,
  TableRow,
  CodeBlock,
  TableCell,
  Paragraph,
  TableBody,
  TableHead,
  InlineCode,
} from './elements';

import type { ReactMarkdownProps } from 'react-markdown';

interface MarkdownProps {
  content: string;
}

const renderers = {
  break: Br,
  link: Link,
  list: List,
  table: Table,
  code: CodeBlock,
  heading: Heading,
  tableRow: TableRow,
  listItem: ListItem,
  tableHead: TableHead,
  tableBody: TableBody,
  paragraph: Paragraph,
  tableCell: TableCell,
  inlineCode: InlineCode,
  thematicBreak: Divider,
} as ReactMarkdownProps['renderers'];

export const Markdown = (props: MarkdownProps): JSX.Element => (
  <ReactMarkdown plugins={[gfm]} renderers={renderers} source={props.content} />
);
