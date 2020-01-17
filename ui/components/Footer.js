import React, { useState } from "react";
import { Flex, useColorMode, useTheme } from "@chakra-ui/core";
import { FiCode } from "react-icons/fi";
import { GoLinkExternal } from "react-icons/go";
import format from "string-format";
import FooterButton from "~/components/FooterButton";
import FooterContent from "~/components/FooterContent";

format.extend(String.prototype, {});

export default ({ general, help, extLink, credit, terms, content }) => {
    const theme = useTheme();
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
    const extUrl = extLink.url.includes("{primary_asn}")
        ? extLink.url.format({ primary_asn: general.primary_asn })
        : extLink.url || "/";
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
            {help.enable && (
                <FooterContent
                    isOpen={helpVisible}
                    content={content.help_menu}
                    title={help.title}
                    bg={footerBg[colorMode]}
                    borderColor={contentBorder[colorMode]}
                    side="left"
                />
            )}
            {terms.enable && (
                <FooterContent
                    isOpen={termsVisible}
                    content={content.terms}
                    title={terms.title}
                    bg={footerBg[colorMode]}
                    borderColor={contentBorder[colorMode]}
                    side="left"
                />
            )}
            {credit.enable && (
                <FooterContent
                    isOpen={creditVisible}
                    content={content.credit}
                    title={credit.title}
                    bg={footerBg[colorMode]}
                    borderColor={contentBorder[colorMode]}
                    side="right"
                />
            )}
            <Flex
                py={2}
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
                {terms.enable && (
                    <FooterButton side="left" onClick={() => handleCollapse("terms")}>
                        {terms.title}
                    </FooterButton>
                )}
                {help.enable && (
                    <FooterButton side="left" onClick={() => handleCollapse("help")}>
                        {help.title}
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
                {credit.enable && (
                    <FooterButton side="right" onClick={() => handleCollapse("credit")}>
                        <FiCode />
                    </FooterButton>
                )}
                {extLink.enable && (
                    <FooterButton
                        as="a"
                        href={extUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        variant="ghost"
                        rightIcon={GoLinkExternal}
                        size="xs"
                    >
                        {extLink.title}
                    </FooterButton>
                )}
            </Flex>
        </>
    );
};
