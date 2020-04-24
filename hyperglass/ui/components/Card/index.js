import * as React from "react";
import { Flex, useColorMode } from "@chakra-ui/core";

const bg = { light: "white", dark: "black" };
const color = { light: "black", dark: "white" };

const Card = ({ onClick = () => false, children, ...props }) => {
  const { colorMode } = useColorMode();
  return (
    <Flex
      w="100%"
      maxW="100%"
      rounded="md"
      borderWidth="1px"
      direction="column"
      onClick={onClick}
      bg={bg[colorMode]}
      color={color[colorMode]}
      {...props}
    >
      {children}
    </Flex>
  );
};

Card.displayName = "Card";

export default Card;
