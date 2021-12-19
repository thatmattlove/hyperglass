import { Box, Flex, SkeletonText, Badge, VStack } from '@chakra-ui/react';
import ReactFlow, { Background, ReactFlowProvider, Handle, Position } from 'react-flow-renderer';
import { useConfig, useColorValue, useColorToken } from '~/context';
import { useASNDetail } from '~/hooks';
import { Controls } from './controls';
import { useElements } from './useElements';

import type { NodeProps as ReactFlowNodeProps } from 'react-flow-renderer';

interface ChartProps {
  data: StructuredResponse;
}

interface NodeProps<D extends unknown> extends Omit<ReactFlowNodeProps, 'data'> {
  data: D;
}

interface NodeData {
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

  return (
    <ReactFlowProvider>
      <Box w="100%" h={{ base: '100vh', lg: '70vh' }} zIndex={1}>
        <ReactFlow
          snapToGrid
          elements={elements}
          nodeTypes={{ ASNode }}
          onLoad={inst => setTimeout(() => inst.fitView(), 0)}
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
  const bg = useColorValue('white', 'whiteAlpha.100');

  const { data: asnData, isError, isLoading } = useASNDetail(String(asn));

  return (
    <>
      {hasChildren && <Handle type="source" position={Position.Top} />}
      <Box py={3} px={4} bg={bg} minW={40} minH={12} color={color} boxShadow="md" borderRadius="md">
        <VStack spacing={4}>
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
