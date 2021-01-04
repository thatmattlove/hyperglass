import dynamic from 'next/dynamic';
import { ButtonGroup, IconButton } from '@chakra-ui/react';
import { useZoomPanHelper } from 'react-flow-renderer';

const Plus = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiPlus));
const Minus = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiMinus));
const Square = dynamic<MeronexIcon>(() => import('@meronex/icons/fi').then(i => i.FiSquare));

export const Controls: React.FC = () => {
  const { fitView, zoomIn, zoomOut } = useZoomPanHelper();
  return (
    <ButtonGroup
      m={4}
      size="sm"
      right={0}
      zIndex={4}
      bottom={0}
      isAttached
      pos="absolute"
      variant="solid"
      colorScheme="secondary"
    >
      <IconButton icon={<Plus />} onClick={() => zoomIn()} aria-label="Zoom In" />
      <IconButton icon={<Minus />} onClick={() => zoomOut()} aria-label="Zoom Out" />
      <IconButton icon={<Square />} onClick={() => fitView()} aria-label="Fit Nodes" />
    </ButtonGroup>
  );
};
