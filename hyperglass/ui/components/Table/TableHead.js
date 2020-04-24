import * as React from "react";
import { Box, useColorMode } from "@chakra-ui/core";

// export const TableHead = styled.div`
//     ${space};
//     display: flex;
//     flex-direction: row;
// `;

const bg = { dark: "whiteAlpha.100", light: "blackAlpha.100" };

const TableHead = ({ children, ...props }) => {
  const { colorMode } = useColorMode();
  return (
    <Box
      as="thead"
      overflowX="hidden"
      overflowY="auto"
      bg={bg[colorMode]}
      {...props}
    >
      {children}
    </Box>
  );
};

TableHead.displayName = "TableHead";

export default TableHead;
