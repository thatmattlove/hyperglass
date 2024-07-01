import { Badge, Box, Flex, SkeletonText, VStack } from '@chakra-ui/react';
import { useMemo } from 'react';
import ReactFlow, {
  Background,
  ReactFlowProvider,
  Handle,
  Position,
  isNode,
  isEdge,
} from 'reactflow';
import { useConfig } from '~/context';
import { useASNDetail, useColorToken, useColorValue } from '~/hooks';
import { Controls } from './controls';
import { useElements } from './use-elements';

import type { NodeProps as ReactFlowNodeProps } from 'reactflow';

interface ChartProps {
  data: StructuredResponse;
}

interface NodeProps<D extends unknown> extends Omit<ReactFlowNodeProps, 'data'> {
  data: D;
}

export interface NodeData {
  asn: string;
  name: string;
  hasChildren: boolean;
  hasParents?: boolean;
}

export const Chart = (props: ChartProps): JSX.Element => {
  const { data } = props;
  const { primaryAsn, orgName } = useConfig();

  const dots = useColorToken('colors', 'blackAlpha.500', 'whiteAlpha.400');

  const elements = useElements({ asn: primaryAsn, name: orgName }, data);

  const nodes = useMemo(() => elements.filter(isNode), [elements]);
  const edges = useMemo(() => elements.filter(isEdge), [elements]);

  return (
    <ReactFlowProvider>
      <Box w="100%" h={{ base: '100vh', lg: '70vh' }} zIndex={1}>
        <ReactFlow
          snapToGrid
          nodes={nodes}
          edges={edges}
          nodeTypes={{ ASNode }}
          edgesUpdatable={false}
          nodesDraggable={false}
          nodesConnectable={false}
          onInit={inst => setTimeout(() => inst.fitView(), 0)}
          proOptions={{ hideAttribution: true }}
        >
          <Background color={dots} />
          <Controls />
        </ReactFlow>
      </Box>
    </ReactFlowProvider>
  );
};

const ASNode = (props: NodeProps<NodeData>): JSX.Element => {
  const { data } = props;
  const { asn, name, hasChildren, hasParents } = data;

  const color = useColorValue('black', 'white');
  const bg = useColorValue('white', 'whiteAlpha.200');

  const { data: asnData, isError, isLoading } = useASNDetail(String(asn));

  return (
    <>
      {hasChildren && <Handle type="source" position={Position.Top} />}
      <Box py={2} px={3} bg={bg} minW={32} minH={8} color={color} boxShadow="md" borderRadius="md">
        <VStack spacing={2}>
          <Flex fontSize="lg">
            {isLoading ? (
              <Box h={2} w={24}>
                <SkeletonText noOfLines={1} color={color} />
              </Box>
            ) : !isError && asnData?.data?.asn.organization?.orgName ? (
              asnData.data.asn.organization.orgName
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
