import { Box, Flex, useDisclosure } from '@chakra-ui/react';
import { FiCode } from '@meronex/icons/fi';
import { GoLinkExternal } from '@meronex/icons/go';
import stringFormat from 'string-format';
import { If } from '~/components';
import { useConfig, useColorValue } from '~/context';
import { FooterButton } from './button';
import { FooterContent } from './content';

export const Footer = () => {
  const { web, content, primary_asn } = useConfig();
  const help = useDisclosure();
  const terms = useDisclosure();
  const credit = useDisclosure();

  const footerBg = useColorValue('blackAlpha.50', 'whiteAlpha.100');
  const footerColor = useColorValue('black', 'white');
  const contentBorder = useColorValue('blackAlpha.100', 'whiteAlpha.200');

  const extUrl = web.external_link.url.includes('{primary_asn}')
    ? stringFormat(web.external_link.url, { primary_asn })
    : web.external_link.url ?? '/';

  return (
    <>
      {web.help_menu.enable && (
        <FooterContent
          content={content.help_menu}
          borderColor={contentBorder}
          bg={footerBg}
          side="left"
          {...help}
        />
      )}
      {web.terms.enable && (
        <FooterContent
          content={content.terms}
          borderColor={contentBorder}
          bg={footerBg}
          side="left"
          {...terms}
        />
      )}
      {web.credit.enable && (
        <FooterContent
          borderColor={contentBorder}
          content={content.credit}
          bg={footerBg}
          side="right"
          {...credit}
        />
      )}
      <Flex
        px={6}
        w="100%"
        as="footer"
        bg={footerBg}
        flexWrap="wrap"
        textAlign="center"
        alignItems="center"
        color={footerColor}
        py={{ base: 4, lg: 2 }}
        justifyContent="space-between">
        <If c={web.terms.enable}>
          <FooterButton side="left" onClick={terms.onToggle} aria-label={web.terms.title}>
            {web.terms.title}
          </FooterButton>
        </If>
        <If c={web.help_menu.enable}>
          <FooterButton side="left" onClick={help.onToggle} aria-label={web.help_menu.title}>
            {web.help_menu.title}
          </FooterButton>
        </If>
        <Flex
          p={0}
          flexGrow={0}
          flexShrink={0}
          maxWidth="100%"
          flexBasis="auto"
          marginRight="auto"
        />
        <If c={web.credit.enable}>
          <FooterButton side="right" onClick={credit.onToggle} aria-label="Powered by hyperglass">
            <FiCode />
          </FooterButton>
        </If>
        <If c={web.external_link.enable}>
          <FooterButton
            size="xs"
            side="right"
            href={extUrl}
            variant="ghost"
            aria-label={web.external_link.title}
            rightIcon={<Box as={GoLinkExternal} />}>
            {web.external_link.title}
          </FooterButton>
        </If>
      </Flex>
    </>
  );
};
