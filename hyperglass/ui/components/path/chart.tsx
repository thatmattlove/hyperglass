import { useMemo } from 'react';
import { Box, Flex, SkeletonText, Badge, VStack } from '@chakra-ui/react';
import ReactFlow from 'react-flow-renderer';
import { Background, ReactFlowProvider } from 'react-flow-renderer';
import { Handle, Position } from 'react-flow-renderer';
import { useConfig, useColorValue, useColorToken, useBreakpointValue } from '~/context';
import { useASNDetail } from '~/hooks';
import { Controls } from './controls';
import { buildElements } from './util';

import type { ReactFlowProps } from 'react-flow-renderer';
import type { TChart, TNode, TNodeData } from './types';

export const Chart: React.FC<TChart> = (props: TChart) => {
  const { data } = props;
  const { primary_asn, org_name } = useConfig();

  const dots = useColorToken('colors', 'blackAlpha.500', 'whiteAlpha.400');

  const flowProps = useBreakpointValue<Omit<ReactFlowProps, 'elements'>>({
    base: { defaultPosition: [0, 300], defaultZoom: 0 },
    lg: { defaultPosition: [100, 300], defaultZoom: 0.7 },
  }) ?? { defaultPosition: [100, 300], defaultZoom: 0.7 };

  const elements = useMemo(() => [...buildElements({ asn: primary_asn, name: org_name }, data)], [
    data,
  ]);

  return (
    <ReactFlowProvider>
      <Box boxSize="100%" zIndex={1}>
        <ReactFlow elements={elements} nodeTypes={{ ASNode }} {...flowProps}>
          <Background color={dots} />
          <Controls />
        </ReactFlow>
      </Box>
    </ReactFlowProvider>
  );
};

const ASNode: React.FC<TNode<TNodeData>> = (props: TNode<TNodeData>) => {
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
