import { useMemo } from 'react';
import { useMeasure } from 'react-use';

import type { UseMeasureRef as UM } from 'react-use/esm/useMeasure';

/**
 * These type aliases are for the readability of the function below.
 */
type DC = HTMLElement;
type DT = HTMLHeadingElement;
type A = any;
type B = boolean;

/**
 * Wrapper for useMeasure() which determines if a text element should be scaled down due to its
 * size relative to its parent's size.
 */
export function useScaledText<C extends DC = DC, T extends DT = DT>(deps: A[]): [UM<C>, UM<T>, B] {
  // Get a ref & state object for the containing element.
  const [containerRef, container] = useMeasure<C>();

  // Get a ref & state object for the text element.
  const [textRef, text] = useMeasure<T>();

  // Memoize the values.
  const textWidth = useMemo(() => text.width, [...deps, text.width !== 0]);
  const containerWidth = useMemo(() => container.width, [...deps, container.width]);

  // If the text element is the same size or larger than the container, it should be resized.
  const shouldResize = textWidth !== 0 && textWidth >= containerWidth;

  return [containerRef, textRef, shouldResize];
}
