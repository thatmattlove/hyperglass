import { Button, Tooltip } from '@chakra-ui/react';
import { DynamicIcon } from '~/elements';

interface PathButtonProps {
  onOpen(): void;
}

export const PathButton = (props: PathButtonProps): JSX.Element => {
  const { onOpen } = props;
  return (
    <Tooltip hasArrow label="View AS Path" placement="top">
      <Button as="a" mx={1} size="sm" variant="ghost" onClick={onOpen} colorScheme="secondary">
        <DynamicIcon icon={{ bi: 'BiNetworkChart' }} boxSize="16px" />
      </Button>
    </Tooltip>
  );
};
