import * as React from "react";
import { Box } from "@chakra-ui/core";
import css from "@styled-system/css";

const TableBody = ({ children, ...props }) => {
  return (
    <Box
      as="tbody"
      overflowY="scroll"
      css={css({
        "&::-webkit-scrollbar": { display: "none" },
        "&": { "-ms-overflow-style": "none" }
      })}
      overflowX="hidden"
      {...props}
    >
      {children}
    </Box>
  );
};

TableBody.displayName = "TableBody";

export default TableBody;
