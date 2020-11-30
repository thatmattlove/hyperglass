import type { ButtonProps, HeadingProps, ImageProps, StackProps } from '@chakra-ui/react';

export interface TTitle extends ButtonProps {}

export interface TTitleOnly extends HeadingProps {
  showSubtitle: boolean;
}

export interface TSubtitleOnly extends HeadingProps {}

export interface TLogo extends ImageProps {}

export interface TTextOnly extends StackProps {
  showSubtitle: boolean;
}
