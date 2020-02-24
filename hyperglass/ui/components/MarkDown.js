import React from "react";
import dynamic from "next/dynamic";
import {
    Checkbox as ChakraCheckbox,
    Divider,
    Code,
    Heading as ChakraHeading,
    Link as ChakraLink,
    List as ChakraList,
    ListItem as ChakraListItem,
    Spinner,
    Text as ChakraText
} from "@chakra-ui/core";
import CustomCodeBlock from "~/components/CodeBlock";
import { TableCell, TableHeader, Table } from "~/components/Table";

// Dynaimc Imports
const ReactMarkdown = dynamic(() => import("react-markdown"), { loading: Spinner });

const Checkbox = ({ checked, children }) => (
    <ChakraCheckbox isChecked={checked}>{children}</ChakraCheckbox>
);

const List = ({ ordered, children }) => (
    <ChakraList as={ordered ? "ol" : "ul"}>{children}</ChakraList>
);

const ListItem = ({ checked, children }) =>
    checked ? (
        <Checkbox checked={checked}>{children}</Checkbox>
    ) : (
        <ChakraListItem>{children}</ChakraListItem>
    );

const Heading = ({ level, children }) => {
    const levelMap = {
        1: { as: "h1", size: "lg", fontWeight: "bold" },
        2: { as: "h2", size: "lg", fontWeight: "normal" },
        3: { as: "h3", size: "lg", fontWeight: "bold" },
        4: { as: "h4", size: "md", fontWeight: "normal" },
        5: { as: "h5", size: "md", fontWeight: "bold" },
        6: { as: "h6", size: "sm", fontWeight: "bold" }
    };
    return <ChakraHeading {...levelMap[level]}>{children}</ChakraHeading>;
};

const Link = ({ children, ...props }) => (
    <ChakraLink isExternal {...props}>
        {children}
    </ChakraLink>
);

const CodeBlock = ({ value }) => <CustomCodeBlock>{value}</CustomCodeBlock>;

const TableData = ({ isHeader, children, ...props }) => {
    const Component = isHeader ? TableHeader : TableCell;
    return <Component {...props}>{children}</Component>;
};

const mdComponents = {
    paragraph: ChakraText,
    link: Link,
    heading: Heading,
    inlineCode: Code,
    list: List,
    listItem: ListItem,
    thematicBreak: Divider,
    code: CodeBlock,
    table: Table,
    tableCell: TableData
};

export default React.forwardRef(({ content }, ref) => (
    <ReactMarkdown ref={ref} renderers={mdComponents} source={content} />
));
