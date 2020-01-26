import React from "react";
import { AccordionIcon, Icon, Spinner, Stack, Text, Tooltip, useColorMode } from "@chakra-ui/core";

export default React.forwardRef(({ title, loading, error, errorMsg, errorLevel }, ref) => {
    const { colorMode } = useColorMode();
    const statusColor = { dark: "primary.300", light: "primary.500" };
    const warningColor = { dark: 300, light: 500 };
    const defaultStatusColor = {
        dark: "success.300",
        light: "success.500"
    };
    return (
        <Stack ref={ref} isInline alignItems="center" w="100%">
            {loading ? (
                <Spinner size="sm" mr={4} color={statusColor[colorMode]} />
            ) : error ? (
                <Tooltip hasArrow label={errorMsg} placement="top">
                    <Icon
                        name="warning"
                        color={`${errorLevel}.${warningColor[colorMode]}`}
                        mr={4}
                        size={6}
                    />
                </Tooltip>
            ) : (
                <Icon name="check" color={defaultStatusColor[colorMode]} mr={4} size={6} />
            )}
            <Text fontSize="lg">{title}</Text>
            <AccordionIcon ml="auto" />
        </Stack>
    );
});
