import type { FlexProps, HeadingProps, ImageProps, StackProps } from '@chakra-ui/react';
import type { MotionProps } from 'framer-motion';

export interface THeader extends FlexProps {
  resetForm(): void;
}

export type THeaderLayout = {
  sm: [JSX.Element, JSX.Element];
  md: [JSX.Element, JSX.Element];
  lg: [JSX.Element, JSX.Element];
  xl: [JSX.Element, JSX.Element];
};
export type TDWrapper = Omit<StackProps, 'transition'> & MotionProps;

export type TMWrapper = Omit<StackProps, 'transition'> & MotionProps;

export interface TTitle extends FlexProps {}

export interface TTitleOnly extends HeadingProps {}

export interface TLogo extends ImageProps {}

export interface TTitleWrapper extends Partial<MotionProps & Omit<StackProps, 'transition'>> {}

export interface THeaderCtx {
  showSubtitle: boolean;
  titleRef: React.MutableRefObject<HTMLHeadingElement>;
}
