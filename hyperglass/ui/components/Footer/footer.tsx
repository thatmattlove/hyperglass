import dynamic from 'next/dynamic';
import { Button, Flex, Link } from '@chakra-ui/react';
import { If } from '~/components';
import { useConfig, useColorValue } from '~/context';
import { useStrf } from '~/hooks';
import { FooterButton } from './button';

const CodeIcon = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiCode));
const ExtIcon = dynamic<MeronexIcon>(() => import('@meronex/icons/go').then(i => i.GoLinkExternal));

export const Footer = () => {
  const { web, content, primary_asn } = useConfig();

  const footerBg = useColorValue('blackAlpha.50', 'whiteAlpha.100');
  const footerColor = useColorValue('black', 'white');

  const extUrl = useStrf(web.external_link.url, { primary_asn }) ?? '/';

  return (
    <Flex
      px={6}
      w="100%"
      zIndex={1}
      as="footer"
      bg={footerBg}
      flexWrap="wrap"
      textAlign="center"
      alignItems="center"
      color={footerColor}
      py={{ base: 4, lg: 2 }}
      justifyContent="space-between">
      <If c={web.terms.enable}>
        <FooterButton side="left" content={content.terms} title={web.terms.title} />
      </If>
      <If c={web.help_menu.enable}>
        <FooterButton side="left" content={content.help_menu} title={web.help_menu.title} />
      </If>
      <Flex p={0} flexGrow={0} flexShrink={0} maxWidth="100%" flexBasis="auto" marginRight="auto" />
      <If c={web.credit.enable}>
        <FooterButton side="right" content={content.credit} title={<CodeIcon />} />
      </If>
      <If c={web.external_link.enable}>
        <Button
          size="xs"
          as={Link}
          isExternal
          href={extUrl}
          variant="ghost"
          rightIcon={<ExtIcon />}
          aria-label={web.external_link.title}>
          {web.external_link.title}
        </Button>
      </If>
    </Flex>
  );
};
