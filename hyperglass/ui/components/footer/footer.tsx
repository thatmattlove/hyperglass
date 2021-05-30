import { useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Flex, Icon, HStack, useToken } from '@chakra-ui/react';
import { If } from '~/components';
import { useConfig, useMobile, useColorValue, useBreakpointValue } from '~/context';
import { useStrf } from '~/hooks';
import { FooterButton } from './button';
import { ColorModeToggle } from './colorMode';
import { FooterLink } from './link';
import { isLink, isMenu } from './types';

import type { ButtonProps, LinkProps } from '@chakra-ui/react';
import type { TLink, TMenu } from '~/types';

const CodeIcon = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiCode));
const ExtIcon = dynamic<MeronexIcon>(() => import('@meronex/icons/go').then(i => i.GoLinkExternal));

function buildItems(links: TLink[], menus: TMenu[]): [(TLink | TMenu)[], (TLink | TMenu)[]] {
  const leftLinks = links.filter(link => link.side === 'left');
  const leftMenus = menus.filter(menu => menu.side === 'left');
  const rightLinks = links.filter(link => link.side === 'right');
  const rightMenus = menus.filter(menu => menu.side === 'right');

  const left = [...leftLinks, ...leftMenus].sort((a, b) => (a.order > b.order ? 1 : -1));
  const right = [...rightLinks, ...rightMenus].sort((a, b) => (a.order > b.order ? 1 : -1));
  return [left, right];
}

export const Footer: React.FC = () => {
  const { web, content, primary_asn } = useConfig();

  const footerBg = useColorValue('blackAlpha.50', 'whiteAlpha.100');
  const footerColor = useColorValue('black', 'white');

  const size = useBreakpointValue({ base: useToken('sizes', 4), lg: useToken('sizes', 6) });

  const isMobile = useMobile();

  const [left, right] = useMemo(() => buildItems(web.links, web.menus), []);

  return (
    <HStack
      px={6}
      py={4}
      w="100%"
      zIndex={1}
      as="footer"
      bg={footerBg}
      whiteSpace="nowrap"
      color={footerColor}
      spacing={{ base: 8, lg: 6 }}
      d={{ base: 'inline-block', lg: 'flex' }}
      overflowY={{ base: 'auto', lg: 'unset' }}
      justifyContent={{ base: 'center', lg: 'space-between' }}
    >
      {left.map(item => {
        if (isLink(item)) {
          const url = useStrf(item.url, { primary_asn }) ?? '/';
          const icon: Partial<ButtonProps & LinkProps> = {};

          if (item.show_icon) {
            icon.rightIcon = <ExtIcon />;
          }
          return <FooterLink key={item.title} href={url} title={item.title} {...icon} />;
        } else if (isMenu(item)) {
          return (
            <FooterButton key={item.title} side="left" content={item.content} title={item.title} />
          );
        }
      })}
      {!isMobile && <Flex p={0} flex="1 0 auto" maxWidth="100%" mr="auto" />}
      {right.map(item => {
        if (isLink(item)) {
          const url = useStrf(item.url, { primary_asn }) ?? '/';
          const icon: Partial<ButtonProps & LinkProps> = {};

          if (item.show_icon) {
            icon.rightIcon = <ExtIcon />;
          }
          return <FooterLink href={url} title={item.title} {...icon} />;
        } else if (isMenu(item)) {
          return <FooterButton side="right" content={item.content} title={item.title} />;
        }
      })}
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
