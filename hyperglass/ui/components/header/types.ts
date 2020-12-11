import { FlexProps } from '@chakra-ui/react';

import { IConfig } from '~/types';

export interface THeader extends FlexProps {
  resetForm(): void;
}

export type TTitleMode = IConfig['web']['text']['title_mode'];

export type THeaderLayout = {
  sm: [JSX.Element, JSX.Element, JSX.Element];
  md: [JSX.Element, JSX.Element, JSX.Element];
  lg: [JSX.Element, JSX.Element, JSX.Element];
  xl: [JSX.Element, JSX.Element, JSX.Element];
};
