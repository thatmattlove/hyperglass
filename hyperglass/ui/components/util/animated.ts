import { chakra } from '@chakra-ui/react';
import { motion } from 'framer-motion';

/**
 * Even though this seems to do nothing, this fixes the issue of Chakra Factory forwarding
 * framer-motion props when it shouldn't.
 *
 * @see https://chakra-ui.com/docs/features/chakra-factory
 */
const shouldForwardProp = () => true;

export const AnimatedDiv = chakra(motion.div, { shouldForwardProp });
export const AnimatedForm = chakra(motion.form, { shouldForwardProp });
