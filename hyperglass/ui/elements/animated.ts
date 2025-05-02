import { chakra } from '@chakra-ui/react';
import { motion } from 'framer-motion';

import type { BoxProps } from '@chakra-ui/react';
import type { CustomDomComponent, Transition, MotionProps } from 'framer-motion';

type MCComponent = Parameters<typeof chakra>[0];
type MCOptions = Parameters<typeof chakra>[1];
type MakeMotionProps<P extends BoxProps> = React.PropsWithChildren<
  Omit<P, 'transition'> & Omit<MotionProps, 'transition'> & { transition?: Transition }
>;

/**
 * Combine `chakra` and `motion` factories.
 *
 * @param component Component or string
 * @param options `chakra` options
 * @returns Chakra component with motion props.
 */
export function motionChakra<P extends BoxProps = BoxProps>(
  component: MCComponent,
  options?: MCOptions,
): CustomDomComponent<MakeMotionProps<P>> {
  // @ts-expect-error I don't know how to fix this.
  return motion<P>(chakra<MCComponent, P>(component, options));
}

export const AnimatedDiv = motionChakra('div');
