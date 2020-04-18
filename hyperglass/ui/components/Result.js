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
    Tooltip,
    Text,
    useColorMode,
} from "@chakra-ui/core";
import styled from "@emotion/styled";
import LightningBolt from "~/components/icons/LightningBolt";
import useAxios from "axios-hooks";
import strReplace from "react-string-replace";
import format from "string-format";
import { startCase } from "lodash";
import useConfig from "~/components/HyperglassProvider";
import useMedia from "~/components/MediaProvider";
import CopyButton from "~/components/CopyButton";
import RequeryButton from "~/components/RequeryButton";
import ResultHeader from "~/components/ResultHeader";
import CacheTimeout from "~/components/CacheTimeout";

format.extend(String.prototype, {});

const FormattedError = ({ keywords, message }) => {
    const patternStr = keywords.map((kw) => `(${kw})`).join("|");
    const pattern = new RegExp(patternStr, "gi");
    let errorFmt;
    try {
        errorFmt = strReplace(message, pattern, (match) => (
            <Text key={match} as="strong">
                {match}
            </Text>
        ));
    } catch (err) {
        errorFmt = <Text as="span">{message}</Text>;
    }
    return <Text as="span">{keywords.length !== 0 ? errorFmt : message}</Text>;
};

const AccordionHeaderWrapper = styled(Flex)`
    justify-content: space-between;
    &:hover {
        background-color: ${(props) => props.hoverBg};
    }
    &:focus {
        box-shadow: "outline";
    }
`;

const statusMap = { success: "success", warning: "warning", error: "warning", danger: "error" };
const bg = { dark: "gray.800", light: "blackAlpha.100" };
const color = { dark: "white", light: "black" };
const selectionBg = { dark: "white", light: "black" };
const selectionColor = { dark: "black", light: "white" };

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
            setComplete,
        },
        ref
    ) => {
        const config = useConfig();
        const { isSm } = useMedia();
        const { colorMode } = useColorMode();
        const [{ data, loading, error }, refetch] = useAxios({
            url: "/api/query/",
            method: "post",
            data: {
                query_location: queryLocation,
                query_type: queryType,
                query_vrf: queryVrf,
                query_target: queryTarget,
            },
            timeout: timeout,
            useCache: false,
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
                .replace(/\n\n/g, "\n");

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

        const cacheLg = (
            <>
                <CacheTimeout timeout={config.cache.timeout} text={config.web.text.cache_prefix} />
                {data?.cached && (
                    <Tooltip
                        hasArrow
                        label={config.web.text.cache_icon.format({ time: data?.timestamp })}
                        placement="top"
                    >
                        <Box ml={1}>
                            <LightningBolt color={color[colorMode]} />
                        </Box>
                    </Tooltip>
                )}
            </>
        );
        const cacheSm = (
            <>
                {data?.cached && (
                    <Tooltip
                        hasArrow
                        label={config.web.text.cache_icon.format({ time: data?.timestamp })}
                        placement="top"
                    >
                        <Box mr={1}>
                            <LightningBolt color={color[colorMode]} />
                        </Box>
                    </Tooltip>
                )}
                <CacheTimeout timeout={config.cache.timeout} text={config.web.text.cache_prefix} />
            </>
        );

        const cacheData = isSm ? cacheSm : cacheLg;

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
                    "&:first-of-type": { borderTop: "none" },
                })}
            >
                <AccordionHeaderWrapper hoverBg="blackAlpha.50">
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
                            runtime={data?.runtime}
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
                        <Flex direction="column" flex="1 0 auto" maxW={error ? "100%" : null}>
                            {data && !error && (
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
                                            color: selectionColor[colorMode],
                                        },
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

                    <Flex direction="row" flexWrap="wrap">
                        <Flex
                            px={3}
                            mt={2}
                            justifyContent={["flex-start", "flex-start", "flex-end", "flex-end"]}
                            flex="1 0 auto"
                        >
                            {data && !error && config.cache.show_text && cacheData}
                        </Flex>
                    </Flex>
                </AccordionPanel>
            </AccordionItem>
        );
    }
);

Result.displayName = "HyperglassQueryResult";
export default Result;
