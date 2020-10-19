import { motion } from 'framer-motion';

export function withAnimation<P>(Component: React.FunctionComponent) {
  return motion.custom<Omit<P, 'transition'>>(Component);
}
