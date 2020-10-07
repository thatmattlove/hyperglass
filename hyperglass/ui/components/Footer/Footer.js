import * as React from 'react';
import { useState } from 'react';
import { Flex, useColorMode } from '@chakra-ui/core';
import { FiCode } from '@meronex/icons/fi';
import { GoLinkExternal } from '@meronex/icons/go';
import format from 'string-format';
import { useConfig } from 'app/context';
import { FooterButton } from './FooterButton';
import { FooterContent } from './FooterContent';

format.extend(String.prototype, {});

const footerBg = { light: 'blackAlpha.50', dark: 'whiteAlpha.100' };
const footerColor = { light: 'black', dark: 'white' };
const contentBorder = { light: 'blackAlpha.100', dark: 'whiteAlpha.200' };

export const Footer = () => {
  const config = useConfig();
  const { colorMode } = useColorMode();
  const [helpVisible, showHelp] = useState(false);
  const [termsVisible, showTerms] = useState(false);
  const [creditVisible, showCredit] = useState(false);
  const handleCollapse = i => {
    if (i === 'help') {
      showTerms(false);
      showCredit(false);
      showHelp(!helpVisible);
    } else if (i === 'credit') {
      showTerms(false);
      showHelp(false);
      showCredit(!creditVisible);
    } else if (i === 'terms') {
      showHelp(false);
      showCredit(false);
      showTerms(!termsVisible);
    }
  };
  const extUrl = config.web.external_link.url.includes('{primary_asn}')
    ? config.web.external_link.url.format({ primary_asn: config.primary_asn })
    : config.web.external_link.url || '/';
  return (
    <>
      {config.web.help_menu.enable && (
        <FooterContent
          isOpen={helpVisible}
          content={config.content.help_menu}
          title={config.web.help_menu.title}
          bg={footerBg[colorMode]}
          borderColor={contentBorder[colorMode]}
          side="left"
        />
      )}
      {config.web.terms.enable && (
        <FooterContent
          isOpen={termsVisible}
          content={config.content.terms}
          title={config.web.terms.title}
          bg={footerBg[colorMode]}
          borderColor={contentBorder[colorMode]}
          side="left"
        />
      )}
      {config.web.credit.enable && (
        <FooterContent
          isOpen={creditVisible}
          content={config.content.credit}
          title={config.web.credit.title}
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
        justifyContent="space-between">
        {config.web.terms.enable && (
          <FooterButton
            side="left"
            onClick={() => handleCollapse('terms')}
            aria-label={config.web.terms.title}>
            {config.web.terms.title}
          </FooterButton>
        )}
        {config.web.help_menu.enable && (
          <FooterButton
            side="left"
            onClick={() => handleCollapse('help')}
            aria-label={config.web.help_menu.title}>
            {config.web.help_menu.title}
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
        {config.web.credit.enable && (
          <FooterButton
            side="right"
            onClick={() => handleCollapse('credit')}
            aria-label="Powered by hyperglass">
            <FiCode />
          </FooterButton>
        )}
        {config.web.external_link.enable && (
          <FooterButton
            as="a"
            href={extUrl}
            aria-label={config.web.external_link.title}
            target="_blank"
            rel="noopener noreferrer"
            variant="ghost"
            rightIcon={GoLinkExternal}
            size="xs">
            {config.web.external_link.title}
          </FooterButton>
        )}
      </Flex>
    </>
  );
};
