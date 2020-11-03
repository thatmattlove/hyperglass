import { useState } from 'react';
import { Box, Flex } from '@chakra-ui/core';
import { FiCode } from '@meronex/icons/fi';
import { GoLinkExternal } from '@meronex/icons/go';
import stringFormat from 'string-format';
import { useConfig, useColorValue } from '~/context';
import { FooterButton } from './FooterButton';
import { FooterContent } from './FooterContent';

export const Footer = () => {
  const config = useConfig();
  const [helpVisible, showHelp] = useState(false);
  const [termsVisible, showTerms] = useState(false);
  const [creditVisible, showCredit] = useState(false);

  const footerBg = useColorValue('blackAlpha.50', 'whiteAlpha.100');
  const footerColor = useColorValue('black', 'white');
  const contentBorder = useColorValue('blackAlpha.100', 'whiteAlpha.200');

  const handleCollapse = (i: TFooterItems) => {
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
    ? stringFormat(config.web.external_link.url, { primary_asn: config.primary_asn })
    : config.web.external_link.url || '/';

  return (
    <>
      {config.web.help_menu.enable && (
        <FooterContent
          isOpen={helpVisible}
          content={config.content.help_menu}
          bg={footerBg}
          borderColor={contentBorder}
          side="left"
        />
      )}
      {config.web.terms.enable && (
        <FooterContent
          isOpen={termsVisible}
          content={config.content.terms}
          bg={footerBg}
          borderColor={contentBorder}
          side="left"
        />
      )}
      {config.web.credit.enable && (
        <FooterContent
          isOpen={creditVisible}
          content={config.content.credit}
          bg={footerBg}
          borderColor={contentBorder}
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
        bg={footerBg}
        color={footerColor}
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
            href={extUrl}
            side="right"
            aria-label={config.web.external_link.title}
            variant="ghost"
            rightIcon={<Box as={GoLinkExternal} />}
            size="xs">
            {config.web.external_link.title}
          </FooterButton>
        )}
      </Flex>
    </>
  );
};
