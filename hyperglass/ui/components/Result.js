import React, { useEffect, useState } from "react";
import {
    AccordionItem,
    AccordionHeader,
    AccordionPanel,
    Alert,
    Box,
    ButtonGroup,
    css,
    Flex,
    Text,
    useTheme,
    useColorMode
} from "@chakra-ui/core";
import styled from "@emotion/styled";
import useAxios from "axios-hooks";
import strReplace from "react-string-replace";
import useConfig from "~/components/HyperglassProvider";
import CopyButton from "~/components/CopyButton";
import RequeryButton from "~/components/RequeryButton";
import ResultHeader from "~/components/ResultHeader";
import { startCase } from "lodash";

const FormattedError = ({ keywords, message }) => {
    if (keywords === null || keywords === undefined) {
        keywords = [];
    }
    const patternStr = `(${keywords.join("|")})`;
    const pattern = new RegExp(patternStr, "gi");
    const errorFmt = strReplace(message, pattern, match => (
        <Text key={match} as="strong">
            {match}
        </Text>
    ));
    return <Text>{keywords.length !== 0 ? errorFmt : message}</Text>;
};

const AccordionHeaderWrapper = styled(Flex)`
    justify-content: space-between;
    &:hover {
        background-color: ${props => props.hoverBg};
    }
    &:focus {
        box-shadow: "outline";
    }
`;

const statusMap = { success: "success", warning: "warning", error: "warning", danger: "error" };

const Result = React.forwardRef(
    (
        {
            device,
            timeout,
            queryLocation,
            queryType,
            queryVrf,
            queryTarget,
            index,
            resultsComplete,
            setComplete
        },
        ref
    ) => {
        const config = useConfig();
        const theme = useTheme();
        const { colorMode } = useColorMode();
        const bg = { dark: theme.colors.gray[800], light: theme.colors.blackAlpha[100] };
        const color = { dark: theme.colors.white, light: theme.colors.black };
        const selectionBg = { dark: theme.colors.white, light: theme.colors.black };
        const selectionColor = { dark: theme.colors.black, light: theme.colors.white };
        const [{ data, loading, error }, refetch] = useAxios({
            url: "/api/query/",
            method: "post",
            data: {
                query_location: queryLocation,
                query_type: queryType,
                query_vrf: queryVrf,
                query_target: queryTarget
            },
            timeout: timeout
        });

        const [isOpen, setOpen] = useState(false);
        const [hasOverride, setOverride] = useState(false);

        const handleToggle = () => {
            setOpen(!isOpen);
            setOverride(true);
        };
        const cleanOutput =
            data &&
            data.output
                .split("\\n")
                .join("\n")
                .replace(/\n\n/g, "");

        const errorKw = (error && error.response?.data?.keywords) || [];

        let errorMsg;
        if (error && error.response?.data?.output) {
            errorMsg = error.response.data.output;
        } else if (error && error.message.startsWith("timeout")) {
            errorMsg = config.messages.request_timeout;
        } else if (error?.response?.statusText) {
            errorMsg = startCase(error.response.statusText);
        } else if (error && error.message) {
            errorMsg = startCase(error.message);
        } else {
            errorMsg = config.messages.general;
        }

        error && console.dir(error);

        const errorLevel =
            (error?.response?.data?.level && statusMap[error.response?.data?.level]) ?? "error";

        useEffect(() => {
            !loading && resultsComplete === null && setComplete(index);
        }, [loading, resultsComplete]);

        useEffect(() => {
            resultsComplete === index && !hasOverride && setOpen(true);
        }, [resultsComplete, index]);
        return (
            <AccordionItem
                isOpen={isOpen}
                isDisabled={loading}
                ref={ref}
                css={css({
                    "&:last-of-type": { borderBottom: "none" },
                    "&:first-of-type": { borderTop: "none" }
                })}
            >
                <AccordionHeaderWrapper hoverBg={theme.colors.blackAlpha[50]}>
                    <AccordionHeader
                        flex="1 0 auto"
                        py={2}
                        _hover={{}}
                        _focus={{}}
                        w="unset"
                        onClick={handleToggle}
                    >
                        <ResultHeader
                            title={device.display_name}
                            loading={loading}
                            error={error}
                            errorMsg={errorMsg}
                            errorLevel={errorLevel}
                        />
                    </AccordionHeader>
                    <ButtonGroup px={3} py={2}>
                        <CopyButton copyValue={cleanOutput} variant="ghost" isDisabled={loading} />
                        <RequeryButton requery={refetch} variant="ghost" isDisabled={loading} />
                    </ButtonGroup>
                </AccordionHeaderWrapper>
                <AccordionPanel
                    pb={4}
                    overflowX="auto"
                    css={css({ WebkitOverflowScrolling: "touch" })}
                >
                    <Flex direction="row" flexWrap="wrap">
                        <Flex direction="column" flex="1 0 auto">
                            {data && (
                                <Box
                                    fontFamily="mono"
                                    mt={5}
                                    mx={2}
                                    p={3}
                                    border="1px"
                                    borderColor="inherit"
                                    rounded="md"
                                    bg={bg[colorMode]}
                                    color={color[colorMode]}
                                    fontSize="sm"
                                    whiteSpace="pre-wrap"
                                    as="pre"
                                    css={css({
                                        "&::selection": {
                                            backgroundColor: selectionBg[colorMode],
                                            color: selectionColor[colorMode]
                                        }
                                    })}
                                >
                                    {cleanOutput}
                                </Box>
                            )}
                            {error && (
                                <Alert rounded="lg" my={2} py={4} status={errorLevel}>
                                    <FormattedError keywords={errorKw} message={errorMsg} />
                                </Alert>
                            )}
                        </Flex>
                    </Flex>
                </AccordionPanel>
            </AccordionItem>
        );
    }
);

Result.displayName = "HyperglassQueryResult";
export default Result;
