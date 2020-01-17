import React from "react";
import {
    Flex,
    FormControl,
    FormLabel,
    FormErrorMessage,
    useTheme,
    useColorMode
} from "@chakra-ui/core";
import HelpModal from "~/components/HelpModal";

export default ({ label, name, error, hiddenLabels, helpIcon, children, ...props }) => {
    const theme = useTheme();
    const { colorMode } = useColorMode();
    const labelColor =
        colorMode === "dark" ? theme.colors.whiteAlpha[600] : theme.colors.blackAlpha[600];
    return (
        <FormControl
            as={Flex}
            flexDirection="column"
            flexGrow={1}
            flexBasis={0}
            w="100%"
            maxW="100%"
            mx={2}
            isInvalid={error && error.message}
            {...props}
        >
            <FormLabel htmlFor={name} color={labelColor} pl={1} opacity={hiddenLabels ? 0 : null}>
                {label}
                {helpIcon?.enable && <HelpModal item={helpIcon} name={name} />}
            </FormLabel>
            {children}
            <FormErrorMessage opacity={hiddenLabels ? 0 : null}>
                {error && error.message}
            </FormErrorMessage>
        </FormControl>
    );
};
