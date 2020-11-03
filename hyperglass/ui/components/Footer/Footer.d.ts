namespace Chakra {
  type ButtonProps = import('@chakra-ui/core').ButtonProps;
  type CollapseProps = import('@chakra-ui/core').CollapseProps;
}

type TFooterSide = 'left' | 'right';

interface IFooterButton extends Chakra.ButtonProps {
  side: TFooterSide;
  href?: string;
}

interface IFooterContent extends Omit<Chakra.CollapseProps, 'children'> {
  isOpen: boolean;
  content: string;
  side: TFooterSide;
  children?: undefined;
}

type TFooterItems = 'help' | 'credit' | 'terms';
