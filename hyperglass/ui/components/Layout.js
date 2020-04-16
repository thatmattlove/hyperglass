import React, { useRef, useState } from "react";
import { Flex, useColorMode, useDisclosure } from "@chakra-ui/core";
import { motion, AnimatePresence } from "framer-motion";
import HyperglassForm from "~/components/HyperglassForm";
import Results from "~/components/Results";
import Header from "~/components/Header";
import Footer from "~/components/Footer";
import Greeting from "~/components/Greeting";
import Meta from "~/components/Meta";
import useConfig from "~/components/HyperglassProvider";
import Debugger from "~/components/Debugger";
import useSessionStorage from "~/hooks/useSessionStorage";

const AnimatedForm = motion.custom(HyperglassForm);

const bg = { light: "white", dark: "black" };
const color = { light: "black", dark: "white" };

const Layout = () => {
    const config = useConfig();
    const { colorMode } = useColorMode();
    const [isSubmitting, setSubmitting] = useState(false);
    const [formData, setFormData] = useState({});
    const [greetingAck, setGreetingAck] = useSessionStorage("hyperglass-greeting-ack", false);
    const containerRef = useRef(null);

    const handleFormReset = () => {
        containerRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
        setSubmitting(false);
    };
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
                <Flex px={2} flex="0 1 auto" flexDirection="column">
                    <Header isSubmitting={isSubmitting} handleFormReset={handleFormReset} />
                </Flex>
                <Flex
                    px={2}
                    py={0}
                    w="100%"
                    as="main"
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
                                greetingAck={greetingAck}
                                setGreetingAck={setGreetingAck}
                            />
                        )}
                    </AnimatePresence>
                </Flex>
                <Footer />
                {config.developer_mode && <Debugger />}
            </Flex>
            {config.web.greeting.enable && !greetingAck && (
                <Greeting
                    greetingConfig={config.web.greeting}
                    content={config.content.greeting}
                    onClickThrough={setGreetingAck}
                />
            )}
        </>
    );
};

Layout.displayName = "HyperglassLayout";
export default Layout;
