import React, { useState } from "react";
import { Flex, useColorMode, useTheme } from "@chakra-ui/core";
import { FiCode } from "react-icons/fi";
import { GoLinkExternal } from "react-icons/go";
import format from "string-format";
import useConfig from "~/components/HyperglassProvider";
import FooterButton from "~/components/FooterButton";
import FooterContent from "~/components/FooterContent";

format.extend(String.prototype, {});

const Footer = () => {
    const theme = useTheme();
    const config = useConfig();
    const { colorMode } = useColorMode();
    const footerBg = { light: theme.colors.blackAlpha[50], dark: theme.colors.whiteAlpha[100] };
    const footerColor = { light: theme.colors.black, dark: theme.colors.white };
    const contentBorder = {
        light: theme.colors.blackAlpha[100],
        dark: theme.colors.whiteAlpha[200]
    };
    const [helpVisible, showHelp] = useState(false);
    const [termsVisible, showTerms] = useState(false);
    const [creditVisible, showCredit] = useState(false);
    const extUrl = config.external_link.url.includes("{primary_asn}")
        ? config.external_link.url.format({ primary_asn: config.primary_asn })
        : config.external_link.url || "/";
    const handleCollapse = i => {
        if (i === "help") {
            showTerms(false);
            showCredit(false);
            showHelp(!helpVisible);
        } else if (i === "credit") {
            showTerms(false);
            showHelp(false);
            showCredit(!creditVisible);
        } else if (i === "terms") {
            showHelp(false);
            showCredit(false);
            showTerms(!termsVisible);
        }
    };
    return (
        <>
            {config.help.enable && (
                <FooterContent
                    isOpen={helpVisible}
                    content={config.content.help_menu}
                    title={config.help.title}
                    bg={footerBg[colorMode]}
                    borderColor={contentBorder[colorMode]}
                    side="left"
                />
            )}
            {config.terms.enable && (
                <FooterContent
                    isOpen={termsVisible}
                    content={config.content.terms}
                    title={config.terms.title}
                    bg={footerBg[colorMode]}
                    borderColor={contentBorder[colorMode]}
                    side="left"
                />
            )}
            {config.credit.enable && (
                <FooterContent
                    isOpen={creditVisible}
                    content={config.content.credit}
                    title={config.credit.title}
                    bg={footerBg[colorMode]}
                    borderColor={contentBorder[colorMode]}
                    side="right"
                />
            )}
            <Flex
                py={[4, 4, 2, 2]}
                px={6}
                w="100%"
                as="footer"
                flexWrap="wrap"
                textAlign="center"
                alignItems="center"
                bg={footerBg[colorMode]}
                color={footerColor[colorMode]}
                justifyContent="space-between"
            >
                {config.terms.enable && (
                    <FooterButton side="left" onClick={() => handleCollapse("terms")}>
                        {config.terms.title}
                    </FooterButton>
                )}
                {config.help.enable && (
                    <FooterButton side="left" onClick={() => handleCollapse("help")}>
                        {config.help.title}
                    </FooterButton>
                )}
                <Flex
                    flexBasis="auto"
                    flexGrow={0}
                    flexShrink={0}
                    maxWidth="100%"
                    marginRight="auto"
                    p={0}
                />
                {config.credit.enable && (
                    <FooterButton side="right" onClick={() => handleCollapse("credit")}>
                        <FiCode />
                    </FooterButton>
                )}
                {config.external_link.enable && (
                    <FooterButton
                        as="a"
                        href={extUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        variant="ghost"
                        rightIcon={GoLinkExternal}
                        size="xs"
                    >
                        {config.external_link.title}
                    </FooterButton>
                )}
            </Flex>
        </>
    );
};

Footer.displayName = "Footer";
export default Footer;
