import { ButtonGroup, IconButton } from '@chakra-ui/react';
import { useZoomPanHelper } from 'react-flow-renderer';
import { DynamicIcon } from '~/components';

export const Controls = (): JSX.Element => {
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
      <IconButton
        icon={<DynamicIcon icon={{ fi: 'FiPlus' }} />}
        onClick={() => zoomIn()}
        aria-label="Zoom In"
      />
      <IconButton
        icon={<DynamicIcon icon={{ fi: 'FiMinus' }} />}
        onClick={() => zoomOut()}
        aria-label="Zoom Out"
      />
      <IconButton
        icon={<DynamicIcon icon={{ fi: 'FiSquare' }} />}
        onClick={() => fitView()}
        aria-label="Fit Nodes"
      />
    </ButtonGroup>
  );
};
