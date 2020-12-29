import { createContext, useContext } from 'react';
import { createState, useState } from '@hookstate/core';
import type { THeaderCtx, THeaderState } from './types';

const HeaderCtx = createContext<THeaderCtx>({
  showSubtitle: true,
  titleRef: {} as React.MutableRefObject<HTMLHeadingElement>,
});

export const HeaderProvider = HeaderCtx.Provider;
export const useHeaderCtx = (): THeaderCtx => useContext(HeaderCtx);

const HeaderState = createState<THeaderState>({ fontSize: '' });
export const useHeader = () => useState<THeaderState>(HeaderState);
