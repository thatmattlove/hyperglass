import { Flex, HStack, useToken } from '@chakra-ui/react';
import { useMemo } from 'react';
import { useConfig } from '~/context';
import { DynamicIcon } from '~/elements';
import { useBreakpointValue, useColorValue, useMobile } from '~/hooks';
import { isLink, isMenu } from '~/types';
import { FooterButton } from './button';
import { ColorModeToggle } from './color-mode';
import { FooterLink } from './link';

import type { ButtonProps, LinkProps } from '@chakra-ui/react';
import type { Link, Menu } from '~/types';

type MenuItems = (Link | Menu)[];

function buildItems(links: Link[], menus: Menu[]): [MenuItems, MenuItems] {
  const leftLinks = links.filter(link => link.side === 'left');
  const leftMenus = menus.filter(menu => menu.side === 'left');
  const rightLinks = links.filter(link => link.side === 'right');
  const rightMenus = menus.filter(menu => menu.side === 'right');

  const left = [...leftLinks, ...leftMenus].sort((a, b) => (a.order > b.order ? 1 : -1));
  const right = [...rightLinks, ...rightMenus].sort((a, b) => (a.order > b.order ? 1 : -1));
  return [left, right];
}

const LinkOnSide = (props: { item: ArrayElement<MenuItems>; side: 'left' | 'right' }) => {
  const { item, side } = props;
  if (isLink(item)) {
    const icon: Partial<ButtonProps & LinkProps> = {};

    if (item.showIcon) {
      icon.rightIcon = <DynamicIcon icon={{ go: 'GoLinkExternal' }} />;
    }
    return <FooterLink key={item.title} href={item.url} title={item.title} {...icon} />;
  }
  if (isMenu(item)) {
    return <FooterButton key={item.title} side={side} content={item.content} title={item.title} />;
  }
};

export const Footer = (): JSX.Element => {
  const { web, content } = useConfig();

  const footerBg = useColorValue('blackAlpha.50', 'whiteAlpha.100');
  const footerColor = useColorValue('black', 'white');

  const size = useBreakpointValue({ base: useToken('sizes', 4), lg: useToken('sizes', 6) });

  const isMobile = useMobile();

  const [left, right] = useMemo(() => buildItems(web.links, web.menus), [web.links, web.menus]);

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
      display={{ base: 'inline-block', lg: 'flex' }}
      overflowY={{ base: 'auto', lg: 'unset' }}
      justifyContent={{ base: 'center', lg: 'space-between' }}
    >
      {left.map(item => (
        <LinkOnSide key={item.title} item={item} side="left" />
      ))}
      {!isMobile && <Flex p={0} flex="1 0 auto" maxWidth="100%" mr="auto" />}
      {right.map(item => (
        <LinkOnSide key={item.title} item={item} side="right" />
      ))}
      {web.credit.enable && (
        <FooterButton
          key="credit"
          side="right"
          content={content.credit}
          title={<DynamicIcon icon={{ fi: 'FiCode' }} boxSize={size} />}
        />
      )}

      <ColorModeToggle size={size} />
    </HStack>
  );
};
