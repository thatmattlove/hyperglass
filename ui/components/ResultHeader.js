import React from "react";
import { Icon, Spinner, Stack, Text, Tooltip, useColorMode, useTheme } from "@chakra-ui/core";

export default React.forwardRef(({ config, title, loading, error }, ref) => {
    const theme = useTheme();
    const { colorMode } = useColorMode();
    const statusColor = { dark: theme.colors.primary[300], light: theme.colors.primary[500] };
    const defaultWarningColor = { dark: theme.colors.danger[300], light: theme.colors.danger[500] };
    const warningColor = { dark: 300, light: 500 };
    const defaultStatusColor = {
        dark: theme.colors.success[300],
        light: theme.colors.success[500]
    };
    return (
        <Stack ref={ref} isInline alignItems="center">
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
        </Stack>
    );
});
