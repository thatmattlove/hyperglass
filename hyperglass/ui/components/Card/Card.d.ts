namespace Chakra {
  type FlexProps = import('@chakra-ui/core').FlexProps;
}

interface ICardBody extends Omit<Chakra.FlexProps, 'onClick'> {
  onClick?: () => boolean;
}

interface ICardFooter extends Chakra.FlexProps {}

interface ICardHeader extends Chakra.FlexProps {}
