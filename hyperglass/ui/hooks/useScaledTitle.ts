import { useEffect, useRef, useState } from 'react';

type ScaledTitleCallback = (f: string) => void;

function getWidthPx<R extends React.MutableRefObject<HTMLElement>>(ref: R) {
  const computedStyle = window.getComputedStyle(ref.current);
  const widthStr = computedStyle.width.replaceAll('px', '');
  const width = parseFloat(widthStr);
  return width;
}

function reducePx(px: number) {
  return px * 0.9;
}

function reducer(val: number, tooBig: () => boolean): number {
  let r = val;
  if (tooBig()) {
    r = reducePx(val);
  }
  return r;
}

/**
 *
 * useScaledTitle(
 *   f => {
 *     setFontsize(f);
 *   },
 *   titleRef,
 *   ref,
 *   [showSubtitle],
 * );
 */
export function useScaledTitle<
  P extends React.MutableRefObject<HTMLDivElement>,
  T extends React.MutableRefObject<HTMLHeadingElement>
>(callback: ScaledTitleCallback, parentRef: P, titleRef: T, deps: any[] = []) {
  console.log(deps);
  const [fontSize, setFontSize] = useState('');
  const calcSize = useRef(0);

  function effect() {
    const computedSize = window.getComputedStyle(titleRef.current).getPropertyValue('font-size');

    const fontPx = parseFloat(computedSize.replaceAll('px', ''));
    calcSize.current = fontPx;

    if (typeof window !== 'undefined') {
      calcSize.current = reducer(
        calcSize.current,
        () => getWidthPx(titleRef) >= getWidthPx(parentRef),
      );

      setFontSize(`${calcSize.current}px`);

      return callback(fontSize);
    }
  }

  return useEffect(effect, [...deps, callback]);
}
