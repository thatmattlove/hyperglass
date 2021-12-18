import { useMemo } from 'react';
import { Flex, HStack, useToken } from '@chakra-ui/react';
import { If, Then } from 'react-if';
import { DynamicIcon } from '~/components';
import { useConfig, useMobile, useColorValue, useBreakpointValue } from '~/context';
import { useStrf } from '~/hooks';
import { FooterButton } from './button';
import { ColorModeToggle } from './colorMode';
import { FooterLink } from './link';
import { isLink, isMenu } from './types';

import type { ButtonProps, LinkProps } from '@chakra-ui/react';
import type { Link, Menu } from '~/types';

function buildItems(links: Link[], menus: Menu[]): [(Link | Menu)[], (Link | Menu)[]] {
  const leftLinks = links.filter(link => link.side === 'left');
  const leftMenus = menus.filter(menu => menu.side === 'left');
  const rightLinks = links.filter(link => link.side === 'right');
  const rightMenus = menus.filter(menu => menu.side === 'right');

  const left = [...leftLinks, ...leftMenus].sort((a, b) => (a.order > b.order ? 1 : -1));
  const right = [...rightLinks, ...rightMenus].sort((a, b) => (a.order > b.order ? 1 : -1));
  return [left, right];
}

export const Footer = (): JSX.Element => {
  const { web, content, primaryAsn } = useConfig();

  const footerBg = useColorValue('blackAlpha.50', 'whiteAlpha.100');
  const footerColor = useColorValue('black', 'white');

  const size = useBreakpointValue({ base: useToken('sizes', 4), lg: useToken('sizes', 6) });

  const isMobile = useMobile();

  const [left, right] = useMemo(() => buildItems(web.links, web.menus), [web.links, web.menus]);

  const strF = useStrf();

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
          const url = strF(item.url, { primaryAsn }, '/');
          const icon: Partial<ButtonProps & LinkProps> = {};

          if (item.showIcon) {
            icon.rightIcon = <DynamicIcon icon={{ go: 'GoLinkExternal' }} />;
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
          const url = strF(item.url, { primaryAsn }, '/');
          const icon: Partial<ButtonProps & LinkProps> = {};

          if (item.showIcon) {
            icon.rightIcon = <DynamicIcon icon={{ go: 'GoLinkExternal' }} />;
          }
          return <FooterLink key={item.title} href={url} title={item.title} {...icon} />;
        } else if (isMenu(item)) {
          return (
            <FooterButton key={item.title} side="right" content={item.content} title={item.title} />
          );
        }
      })}
      <If condition={web.credit.enable}>
        <Then>
          <FooterButton
            key="credit"
            side="right"
            content={content.credit}
            title={<DynamicIcon icon={{ fi: 'FiCode' }} boxSize={size} />}
          />
        </Then>
      </If>
      <ColorModeToggle size={size} />
    </HStack>
  );
};
