import React from "react";
import { Accordion, Box, Stack, useColorMode, useTheme } from "@chakra-ui/core";
import { motion, AnimatePresence } from "framer-motion";
import Label from "~/components/Label";
import Result from "~/components/Result";

const AnimatedResult = motion.custom(Result);
const AnimatedLabel = motion.custom(Label);

export default ({
    config,
    queryLocation,
    queryType,
    queryVrf,
    queryTarget,
    setSubmitting,
    ...props
}) => {
    const theme = useTheme();
    const { colorMode } = useColorMode();
    const matchedVrf = config.vrfs.filter(v => v.id === queryVrf)[0];
    const labelColor = { light: theme.colors.white, dark: theme.colors.black };
    return (
        <>
            <Box
                maxW={["100%", "100%", "75%", "50%"]}
                w="100%"
                p={0}
                mx="auto"
                my={4}
                textAlign="left"
                {...props}
            >
                <Stack isInline align="center" justify="center" mt={4}>
                    <AnimatePresence>
                        {queryLocation && (
                            <>
                                <AnimatedLabel
                                    initial={{ opacity: 0, x: -100 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.3, delay: 0.3 }}
                                    exit={{ opacity: 0, x: -100 }}
                                    label={config.branding.text.query_type}
                                    value={config.branding.text[queryType]}
                                    valueBg={theme.colors.cyan[500]}
                                    labelColor={labelColor[colorMode]}
                                />
                                <AnimatedLabel
                                    initial={{ opacity: 0, scale: 0.5 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ duration: 0.3, delay: 0.3 }}
                                    exit={{ opacity: 0, scale: 0.5 }}
                                    label={config.branding.text.query_target}
                                    value={queryTarget}
                                    valueBg={theme.colors.teal[600]}
                                    labelColor={labelColor[colorMode]}
                                />
                                <AnimatedLabel
                                    initial={{ opacity: 0, x: 100 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.3, delay: 0.3 }}
                                    exit={{ opacity: 0, x: 100 }}
                                    label={config.branding.text.query_vrf}
                                    value={matchedVrf.display_name}
                                    valueBg={theme.colors.blue[500]}
                                    labelColor={labelColor[colorMode]}
                                />
                            </>
                        )}
                    </AnimatePresence>
                </Stack>
            </Box>
            <Box
                maxW={["100%", "100%", "75%", "50%"]}
                w="100%"
                p={0}
                mx="auto"
                my={4}
                textAlign="left"
                borderWidth="1px"
                rounded="lg"
                overflow="hidden"
            >
                <Accordion
                    initial={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 300 }}
                >
                    <AnimatePresence>
                        {queryLocation &&
                            queryLocation.map((loc, i) => (
                                <AnimatedResult
                                    config={config}
                                    initial={{ opacity: 0, y: 300 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.3, delay: i * 0.3 }}
                                    exit={{ opacity: 0, y: 300 }}
                                    key={loc}
                                    timeout={config.general.request_timeout * 1000}
                                    device={config.devices[loc]}
                                    queryLocation={loc}
                                    queryType={queryType}
                                    queryVrf={queryVrf}
                                    queryTarget={queryTarget}
                                    setSubmitting={setSubmitting}
                                />
                            ))}
                    </AnimatePresence>
                </Accordion>
            </Box>
        </>
    );
};
