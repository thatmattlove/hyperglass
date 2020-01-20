import React from "react";
import {
    AccordionIcon,
    Icon,
    Spinner,
    Stack,
    Text,
    Tooltip,
    useColorMode,
    useTheme
} from "@chakra-ui/core";
import useConfig from "~/components/HyperglassProvider";

export default React.forwardRef(({ title, loading, error }, ref) => {
    const config = useConfig();
    const theme = useTheme();
    const { colorMode } = useColorMode();
    const statusColor = { dark: "primary.300", light: "primary.500" };
    const defaultWarningColor = { dark: "danger.300", light: "danger.500" };
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
                <Tooltip
                    hasArrow
                    label={error.response?.data?.output || error.message || config.messages.general}
                    placement="top"
                >
                    <Icon
                        name="warning"
                        color={
                            error.response
                                ? theme.colors[error.response?.data?.alert][warningColor[colorMode]]
                                : defaultWarningColor[colorMode]
                        }
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
