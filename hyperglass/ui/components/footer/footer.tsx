import dynamic from 'next/dynamic';
import { Button, Flex, Link, Icon, HStack, useToken } from '@chakra-ui/react';
import { If } from '~/components';
import { useConfig, useMobile, useColorValue, useBreakpointValue } from '~/context';
import { useStrf } from '~/hooks';
import { FooterButton } from './button';
import { ColorModeToggle } from './colorMode';

const CodeIcon = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiCode));
const ExtIcon = dynamic<MeronexIcon>(() => import('@meronex/icons/go').then(i => i.GoLinkExternal));

export const Footer: React.FC = () => {
  const { web, content, primary_asn } = useConfig();

  const footerBg = useColorValue('blackAlpha.50', 'whiteAlpha.100');
  const footerColor = useColorValue('black', 'white');

  const extUrl = useStrf(web.external_link.url, { primary_asn }) ?? '/';

  const size = useBreakpointValue({ base: useToken('sizes', 4), lg: useToken('sizes', 6) });
  const btnSize = useBreakpointValue({ base: 'xs', lg: 'sm' });

  const isMobile = useMobile();

  return (
    <HStack
      px={6}
      py={4}
      w="100%"
      zIndex={1}
      as="footer"
      bg={footerBg}
      color={footerColor}
      spacing={{ base: 8, lg: 6 }}
      justifyContent={{ base: 'center', lg: 'space-between' }}
    >
      <If c={web.terms.enable}>
        <FooterButton side="left" content={content.terms} title={web.terms.title} />
      </If>
      <If c={web.help_menu.enable}>
        <FooterButton side="left" content={content.help_menu} title={web.help_menu.title} />
      </If>
      <If c={web.external_link.enable}>
        <Button
          as={Link}
          isExternal
          href={extUrl}
          size={btnSize}
          variant="ghost"
          rightIcon={<ExtIcon />}
          aria-label={web.external_link.title}
        >
          {web.external_link.title}
        </Button>
      </If>
      {!isMobile && <Flex p={0} flex="0 0 auto" maxWidth="100%" mr="auto" />}
      <If c={web.credit.enable}>
        <FooterButton
          side="right"
          content={content.credit}
          title={<Icon as={CodeIcon} boxSize={size} />}
        />
      </If>
      <ColorModeToggle size={size} />
    </HStack>
  );
};
