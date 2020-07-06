import * as React from "react";
import { forwardRef } from "react";
import { Box, Collapse } from "@chakra-ui/core";
import MarkDown from "~/components/MarkDown";

const FooterContent = forwardRef(
  ({ isOpen = false, content, side = "left", title, ...props }, ref) => {
    return (
      <Collapse
        px={6}
        py={4}
        w="auto"
        ref={ref}
        borderBottom="1px"
        display="flex"
        maxWidth="100%"
        isOpen={isOpen}
        flexBasis="auto"
        justifyContent={side === "left" ? "flex-start" : "flex-end"}
        {...props}
      >
        <Box textAlign={side}>
          <MarkDown content={content} />
        </Box>
      </Collapse>
    );
  }
);

export default FooterContent;
