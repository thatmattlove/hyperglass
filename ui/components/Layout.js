import React, { useState } from "react";
import { Flex, useColorMode, useTheme } from "@chakra-ui/core";
import { motion, AnimatePresence } from "framer-motion";
import ResetButton from "~/components/ResetButton";
import HyperglassForm from "~/components/HyperglassForm";
import Results from "~/components/Results";
import Header from "~/components/Header";
import Footer from "~/components/Footer";
import Title from "~/components/Title";
import Meta from "~/components/Meta";

const AnimatedForm = motion.custom(HyperglassForm);
const AnimatedTitle = motion.custom(Title);
const AnimatedResetButton = motion.custom(ResetButton);

export default ({ config }) => {
    const theme = useTheme();
    const { colorMode } = useColorMode();
    const bg = { light: theme.colors.white, dark: theme.colors.black };
    const color = { light: theme.colors.black, dark: theme.colors.white };
    const [isSubmitting, setSubmitting] = useState(false);
    const [formData, setFormData] = useState({});
    const handleFormReset = () => {
        setSubmitting(false);
    };
    return (
        <>
            <Meta config={config} />
            <Flex
                flexDirection="column"
                minHeight="100vh"
                w="100%"
                bg={bg[colorMode]}
                color={color[colorMode]}
            >
                <Header />
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
                    mt={["5%", "5%", "5%", "10%"]}
                >
                    <AnimatePresence>
                        <AnimatedTitle
                            initial={{ opacity: 0, y: -300 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                            exit={{ opacity: 0, y: -300 }}
                            text={config.branding.text}
                            logo={config.branding.logo}
                            resetForm={handleFormReset}
                        />
                    </AnimatePresence>
                    {isSubmitting && formData && (
                        <Results
                            config={config}
                            queryLocation={formData.query_location}
                            queryType={formData.query_type}
                            queryVrf={formData.query_vrf}
                            queryTarget={formData.query_target}
                            setSubmitting={setSubmitting}
                        />
                    )}
                    <AnimatePresence>
                        {!isSubmitting && (
                            <AnimatedForm
                                initial={{ opacity: 0, y: 300 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3 }}
                                exit={{ opacity: 0, x: -300 }}
                                config={config}
                                isSubmitting={isSubmitting}
                                setSubmitting={setSubmitting}
                                setFormData={setFormData}
                            />
                        )}
                    </AnimatePresence>
                </Flex>
                <AnimatePresence>
                    {isSubmitting && (
                        <AnimatedResetButton
                            initial={{ opacity: 0, x: -50 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3 }}
                            exit={{ opacity: 0, x: -50 }}
                            isSubmitting={isSubmitting}
                            onClick={handleFormReset}
                        />
                    )}
                </AnimatePresence>
                <Footer
                    general={config.general}
                    content={config.content}
                    terms={config.branding.terms}
                    help={config.branding.help_menu}
                    credit={config.branding.credit}
                    extLink={config.branding.external_link}
                />
            </Flex>
        </>
    );
};
