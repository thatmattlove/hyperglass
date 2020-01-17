import React from "react";
import {
    AccordionItem,
    AccordionHeader,
    AccordionPanel,
    AccordionIcon,
    Alert,
    Box,
    ButtonGroup,
    Flex,
    Text,
    useTheme,
    useColorMode
} from "@chakra-ui/core";
import styled from "@emotion/styled";
import useAxios from "axios-hooks";
import strReplace from "react-string-replace";
import CopyButton from "~/components/CopyButton";
import RequeryButton from "~/components/RequeryButton";
import ResultHeader from "~/components/ResultHeader";

const PreBox = styled(Box)`
    &::selection {
        background-color: ${props => props.selectionBg};
        color: ${props => props.selectionColor};
    }
`;

const FormattedError = ({ keywords, message }) => {
    const patternStr = `(${keywords.join("|")})`;
    const pattern = new RegExp(patternStr, "gi");
    const errorFmt = strReplace(message, pattern, match => <Text as="strong">{match}</Text>);
    return <Text>{errorFmt}</Text>;
};

export default React.forwardRef(
    ({ config, device, timeout, queryLocation, queryType, queryVrf, queryTarget }, ref) => {
        const theme = useTheme();
        const { colorMode } = useColorMode();
        const bg = { dark: theme.colors.gray[800], light: theme.colors.blackAlpha[100] };
        const color = { dark: theme.colors.white, light: theme.colors.black };
        const selectionBg = { dark: theme.colors.white, light: theme.colors.black };
        const selectionColor = { dark: theme.colors.black, light: theme.colors.white };
        const [{ data, loading, error }, refetch] = useAxios({
            url: "/query",
            method: "post",
            data: {
                query_location: queryLocation,
                query_type: queryType,
                query_vrf: queryVrf,
                query_target: queryTarget
            },
            timeout: timeout
        });
        const cleanOutput =
            data &&
            data.output
                .split("\\n")
                .join("\n")
                .replace(/\n\n/g, "");

        const errorKw = (error && error.response?.data?.keywords) || [];
        const errorMsg =
            (error && error.response?.data?.output) ||
            (error && error.message) ||
            config.messages.general;
        return (
            <AccordionItem
                isDisabled={loading}
                ref={ref}
                css={{
                    "&:last-of-type": { borderBottom: "none" },
                    "&:first-of-type": { borderTop: "none" }
                }}
            >
                <AccordionHeader justifyContent="space-between">
                    <ResultHeader
                        config={config}
                        title={device.display_name}
                        loading={loading}
                        error={error}
                    />
                    <Flex>
                        <AccordionIcon />
                    </Flex>
                </AccordionHeader>
                <AccordionPanel pb={4}>
                    <Box position="relative">
                        {data && (
                            <PreBox
                                fontFamily="mono"
                                mt={5}
                                p={3}
                                border="1px"
                                borderColor="inherit"
                                rounded="md"
                                bg={bg[colorMode]}
                                color={color[colorMode]}
                                fontSize="sm"
                                whiteSpace="pre-wrap"
                                as="pre"
                                selectionBg={selectionBg[colorMode]}
                                selectionColor={selectionColor[colorMode]}
                            >
                                {cleanOutput}
                            </PreBox>
                        )}
                        {error && (
                            <Alert
                                rounded="lg"
                                my={2}
                                py={4}
                                status={error.response?.data?.alert || "error"}
                            >
                                <FormattedError keywords={errorKw} message={errorMsg} />
                            </Alert>
                        )}
                        <ButtonGroup position="absolute" top={0} right={5} py={3} spacing={4}>
                            <CopyButton copyValue={cleanOutput} />
                            <RequeryButton isLoading={loading} requery={refetch} />
                        </ButtonGroup>
                    </Box>
                </AccordionPanel>
            </AccordionItem>
        );
    }
);
