import * as React from 'react';
import { forwardRef } from 'react';
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

export const Markdown = forwardRef(({ content }, ref) => (
  <ReactMarkdown ref={ref} renderers={mdComponents} source={content} />
));
