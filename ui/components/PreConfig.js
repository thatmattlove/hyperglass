import React from "react";
import { Button, Flex, Heading, Spinner, useTheme, useColorMode } from "@chakra-ui/core";

const ErrorMsg = ({ title }) => (
    <>
        <Heading mb={4} color="danger.500" as="h1" fontSize="2xl">
            {title}
        </Heading>
    </>
);

const ErrorBtn = ({ text, onClick }) => (
    <Button variant="outline" variantColor="danger" onClick={onClick}>
        {text}
    </Button>
);

export default ({ loading, error, refresh }) => {
    const theme = useTheme();
    const { colorMode } = useColorMode();
    const bg = { light: theme.colors.white, dark: theme.colors.dark };
    const color = { light: theme.colors.dark, dark: theme.colors.white };
    return (
        <Flex
            flexDirection="column"
            minHeight="100vh"
            w="100%"
            bg={bg[colorMode]}
            color={color[colorMode]}
        >
            <Flex
                as="main"
                w="100%"
                flexGrow={1}
                flexShrink={1}
                flexBasis="auto"
                alignItems="center"
                justifyContent="start"
                textAlign="center"
                flexDirection="column"
                px={2}
                py={0}
                mt={["50%", "50%", "50%", "25%"]}
            >
                {loading && <Spinner color="primary.500" w="6rem" h="6rem" />}
                {!loading && error && (
                    <>
                        <ErrorMsg
                            title={
                                error.response?.data?.output || error.message || "An Error Occurred"
                            }
                        />
                        <ErrorBtn text="Retry" onClick={refresh} />
                    </>
                )}
            </Flex>
        </Flex>
    );
};
