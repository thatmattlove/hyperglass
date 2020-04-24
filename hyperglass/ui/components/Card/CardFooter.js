import * as React from "react";
import { Flex } from "@chakra-ui/core";

const CardFooter = ({ children, ...props }) => {
  return (
    <Flex
      p={4}
      roundedBottomLeft={4}
      roundedBottomRight={4}
      direction="column"
      borderTopWidth="1px"
      overflowX="hidden"
      overflowY="hidden"
      flexDirection="row"
      justifyContent="space-between"
      {...props}
    >
      {children}
    </Flex>
  );
};

CardFooter.displayName = "CardFooter";

export default CardFooter;
