import React, { useRef, useState } from "react";
import { Flex, useColorMode } from "@chakra-ui/core";
import { motion, AnimatePresence } from "framer-motion";
import HyperglassForm from "~/components/HyperglassForm";
import Results from "~/components/Results";
import Header from "~/components/Header";
import Footer from "~/components/Footer";
import Meta from "~/components/Meta";
import useConfig from "~/components/HyperglassProvider";
import Debugger from "~/components/Debugger";

const AnimatedForm = motion.custom(HyperglassForm);

const bg = { light: "white", dark: "black" };
const color = { light: "black", dark: "white" };
const headerHeightDefault = { true: [16, 16, 16, 16], false: [24, 64, 64, 64] };
const headerHeightAll = { true: [32, 32, 32, 32], false: [48, "20rem", "20rem", "20rem"] };

const Layout = () => {
    const config = useConfig();
    const { colorMode } = useColorMode();
    const [isSubmitting, setSubmitting] = useState(false);
    const [formData, setFormData] = useState({});
    const containerRef = useRef(null);
    const handleFormReset = () => {
        containerRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
        setSubmitting(false);
    };
    const headerHeight =
        config.web.text.title_mode === "all"
            ? headerHeightAll[isSubmitting]
            : headerHeightDefault[isSubmitting];
    return (
        <>
            <Meta />
            <Flex
                w="100%"
                ref={containerRef}
                minHeight="100vh"
                bg={bg[colorMode]}
                flexDirection="column"
                color={color[colorMode]}
            >
                <Flex px={2} flex="1 1 auto" flexGrow={0} flexDirection="column">
                    <Header
                        isSubmitting={isSubmitting}
                        handleFormReset={handleFormReset}
                        height={headerHeight}
                    />
                </Flex>
                <Flex
                    px={2}
                    py={0}
                    w="100%"
                    as="main"
                    mt={headerHeight}
                    flex="1 1 auto"
                    textAlign="center"
                    alignItems="center"
                    justifyContent="start"
                    flexDirection="column"
                >
                    {isSubmitting && formData && (
                        <Results
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
                                isSubmitting={isSubmitting}
                                setSubmitting={setSubmitting}
                                setFormData={setFormData}
                            />
                        )}
                    </AnimatePresence>
                </Flex>
                <Footer />
                {config.developer_mode && <Debugger />}
            </Flex>
        </>
    );
};

Layout.displayName = "HyperglassLayout";
export default Layout;
