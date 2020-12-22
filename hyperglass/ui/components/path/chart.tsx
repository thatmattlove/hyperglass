import { useMemo } from 'react';
import { Box, Flex, Icon, Badge, VStack } from '@chakra-ui/react';
import { BeatLoader } from 'react-spinners';
import ReactFlow from 'react-flow-renderer';
import { Background, Controls } from 'react-flow-renderer';
import { Handle, Position } from 'react-flow-renderer';
import { useConfig, useColorValue, useColorToken } from '~/context';
import { useASNDetail } from '~/hooks';
import { buildElements } from './util';

import type { TChart, TNode, TNodeData } from './types';

export const Chart = (props: TChart) => {
  const { data } = props;
  const { primary_asn, org_name } = useConfig();
  // const elements = useMemo(() => [...buildElements({ asn: primary_asn, name: org_name }, data)], [
  //   data,
  // ]);

  const elements = [...buildElements({ asn: primary_asn, name: org_name }, data)];
  const dots = useColorToken('blackAlpha.500', 'whiteAlpha.400');
  return (
    <Box boxSize="100%">
      <ReactFlow elements={elements} nodeTypes={{ TestNode }} defaultPosition={[500, 450]}>
        <Background color={dots} />
        <Controls />
      </ReactFlow>
    </Box>
  );
};

const TestNode = (props: TNode<TNodeData>) => {
  const { data } = props;
  const { asn, name, hasChildren, hasParents } = data;
  const color = useColorValue('black', 'white');
  const bg = useColorValue('white', 'blackAlpha.800');
  const { data: asnData, isError, isLoading } = useASNDetail(asn);
  return (
    <>
      {hasChildren && <Handle type="source" position={Position.Top} />}
      <Box py={3} px={4} bg={bg} minW={40} minH={12} color={color} boxShadow="md" borderRadius="md">
        <VStack spacing={4}>
          <Flex fontSize="lg">
            {isLoading ? (
              <BeatLoader color={color} />
            ) : !isError && asnData?.data?.description_short ? (
              asnData.data.description_short
            ) : (
              name
            )}
          </Flex>
          <Badge fontFamily="mono" fontWeight="normal" fontSize="sm" colorScheme="primary">
            {asn}
          </Badge>
        </VStack>
      </Box>
      {hasParents && <Handle type="target" position={Position.Bottom} />}
    </>
  );
};
