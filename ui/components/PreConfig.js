import React from "react";
import {
    Button,
    ColorModeProvider,
    CSSReset,
    Flex,
    Heading,
    Spinner,
    ThemeProvider,
    useTheme,
    useColorMode
} from "@chakra-ui/core";
import { defaultTheme } from "~/theme";

const PreConfig = ({ loading, error, refresh }) => {
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
                        <Heading mb={4} color="danger.500" as="h1" fontSize="2xl">
                            {error.response?.data?.output || error.message || "An Error Occurred"}
                        </Heading>
                        <Button variant="outline" variantColor="danger" onClick={refresh}>
                            Retry
                        </Button>
                    </>
                )}
            </Flex>
        </Flex>
    );
};

export default ({ loading, error, refresh }) => {
    return (
        <ThemeProvider theme={defaultTheme}>
            <ColorModeProvider>
                <CSSReset />
                <PreConfig loading={loading} error={error} refresh={refresh} />
            </ColorModeProvider>
        </ThemeProvider>
    );
};
