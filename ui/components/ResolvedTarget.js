import React, { useEffect, useState } from "react";
import { Button, Icon, Spinner, Stack, Tag, Text, Tooltip, useColorMode } from "@chakra-ui/core";
import useAxios from "axios-hooks";
import format from "string-format";
import useConfig from "~/components/HyperglassProvider";

format.extend(String.prototype, {});

const labelBg = { dark: "secondary", light: "secondary" };
const labelBgSuccess = { dark: "success", light: "success" };

const ResolvedTarget = React.forwardRef(({ fqdnTarget, setTarget, queryTarget }, ref) => {
    const { colorMode } = useColorMode();
    const config = useConfig();
    const labelBgStatus = { true: labelBgSuccess[colorMode], false: labelBg[colorMode] };
    const dnsUrl = config.web.dns_provider.url;
    const params4 = {
        url: dnsUrl,
        params: { name: fqdnTarget, type: "A" },
        headers: { accept: "application/dns-json" },
        timeout: 1000
    };
    const params6 = {
        url: dnsUrl,
        params: { name: fqdnTarget, type: "AAAA" },
        headers: { accept: "application/dns-json" },
        timeout: 1000
    };

    const [{ data: data4, loading: loading4, error: error4 }] = useAxios(params4);
    const [{ data: data6, loading: loading6, error: error6 }] = useAxios(params6);

    const handleOverride = overridden => {
        setTarget({ field: "query_target", value: overridden });
    };

    const isSelected = value => {
        return labelBgStatus[value === queryTarget];
    };

    useEffect(() => {
        if (data6 && data6.Answer && data6.Answer[0].type === 28) {
            handleOverride(data6.Answer[0].data);
        } else if (data4 && data4.Answer && data4.Answer[0].type === 1 && !data6?.Answer) {
            handleOverride(data4.Answer[0].data);
        }
    }, [data4, data6]);
    return (
        <Stack
            ref={ref}
            isInline
            w="100%"
            justifyContent={data4?.Answer && data6?.Answer ? "space-between" : "flex-end"}
        >
            {loading4 ||
                error4 ||
                (data4?.Answer?.[0] && (
                    <Tag>
                        <Tooltip
                            hasArrow
                            label={config.web.text.fqdn_tooltip.format({ protocol: "IPv4" })}
                            placement="bottom"
                        >
                            <Button
                                height="unset"
                                minW="unset"
                                fontSize="xs"
                                py="0.1rem"
                                px={2}
                                mr={2}
                                variantColor={labelBgStatus[data4.Answer[0].data === queryTarget]}
                                borderRadius="md"
                                onClick={() => handleOverride(data4.Answer[0].data)}
                            >
                                IPv4
                            </Button>
                        </Tooltip>
                        {loading4 && <Spinner />}
                        {error4 && <Icon name="warning" />}
                        {data4?.Answer?.[0] && (
                            <Text fontSize="xs" fontFamily="mono" as="span" fontWeight={400}>
                                {data4.Answer[0].data}
                            </Text>
                        )}
                    </Tag>
                ))}
            {loading6 ||
                error6 ||
                (data6?.Answer?.[0] && (
                    <Tag>
                        <Tooltip
                            hasArrow
                            label={config.web.text.fqdn_tooltip.format({ protocol: "IPv6" })}
                            placement="bottom"
                        >
                            <Button
                                height="unset"
                                minW="unset"
                                fontSize="xs"
                                py="0.1rem"
                                px={2}
                                mr={2}
                                variantColor={isSelected(data6.Answer[0].data)}
                                borderRadius="md"
                                onClick={() => handleOverride(data6.Answer[0].data)}
                            >
                                IPv6
                            </Button>
                        </Tooltip>
                        {loading6 && <Spinner />}
                        {error6 && <Icon name="warning" />}
                        {data6?.Answer?.[0] && (
                            <Text fontSize="xs" fontFamily="mono" as="span" fontWeight={400}>
                                {data6.Answer[0].data}
                            </Text>
                        )}
                    </Tag>
                ))}
        </Stack>
    );
});

ResolvedTarget.displayName = "ResolvedTarget";
export default ResolvedTarget;
