import dagre from 'dagre';
import { useMemo } from 'react';
import isEqual from 'react-fast-compare';

import type { Edge, Node } from 'reactflow';
import type { NodeData } from './chart';

interface BasePath {
  asn: string;
  name: string;
}

type FlowElement<T> = Node<T> | Edge<T>;

const NODE_WIDTH = 128;
const NODE_HEIGHT = 48;

export function useElements(base: BasePath, data: AllStructuredResponses): FlowElement<NodeData>[] {
  return useMemo(() => {
    return [...buildElements(base, data)];
  }, [base, data]);
}

/**
 * Check if data contains BGP routes
 */
function isBGPData(data: AllStructuredResponses): data is BGPStructuredOutput {
  return 'routes' in data && Array.isArray(data.routes);
}

/**
 * Check if data contains traceroute hops
 */
function isTracerouteData(data: AllStructuredResponses): data is TracerouteStructuredOutput {
  return 'hops' in data && Array.isArray(data.hops);
}

/**
 * Calculate the positions for each AS Path.
 * @see https://github.com/MrBlenny/react-flow-chart/issues/61
 */
function* buildElements(
  base: BasePath,
  data: AllStructuredResponses,
): Generator<FlowElement<NodeData>> {
  let asPaths: string[][] = [];
  let asnOrgs: Record<string, { name: string; country: string }> = {};

  if (isBGPData(data)) {
    // Handle BGP routes with AS paths
    const { routes } = data;
    asPaths = routes
      .filter(r => r.as_path.length !== 0)
      .map(r => {
        const uniqueAsns = [...new Set(r.as_path.map(asn => String(asn)))];
        // Remove the base ASN if it's the first hop to avoid duplication
        return uniqueAsns[0] === base.asn ? uniqueAsns.slice(1) : uniqueAsns;
      })
      .filter(path => path.length > 0); // Remove empty paths
    
    // Get ASN organization mapping if available
    asnOrgs = (data as any).asn_organizations || {};
    
    // Debug: Log BGP ASN organization data
    if (Object.keys(asnOrgs).length > 0) {
      console.debug('BGP ASN organizations loaded:', asnOrgs);
    } else {
      console.warn('BGP ASN organizations not found or empty');
    }
  } else if (isTracerouteData(data)) {
    // Handle traceroute hops - build AS path from hop ASNs
    const hopAsns: string[] = [];
    let currentAsn = '';
    
    for (const hop of data.hops) {
      if (hop.asn && hop.asn !== 'None' && hop.asn !== currentAsn) {
        currentAsn = hop.asn;
        hopAsns.push(hop.asn);
      }
    }
    
    if (hopAsns.length > 0) {
      // Remove the base ASN if it's the first hop to avoid duplication
      const filteredAsns = hopAsns[0] === base.asn ? hopAsns.slice(1) : hopAsns;
      if (filteredAsns.length > 0) {
        asPaths = [filteredAsns];
      }
    }
    
    // Get ASN organization mapping if available
    asnOrgs = (data as any).asn_organizations || {};
    
    // Debug: Log traceroute ASN organization data
    if (Object.keys(asnOrgs).length > 0) {
      console.debug('Traceroute ASN organizations loaded:', asnOrgs);
    } else {
      console.warn('Traceroute ASN organizations not found or empty');
    }
  }

  if (asPaths.length === 0) {
    return;
  }

  const totalPaths = asPaths.length - 1;

  const g = new dagre.graphlib.Graph();
  g.setGraph({ marginx: 20, marginy: 20 });
  g.setDefaultEdgeLabel(() => ({}));

  // Set the origin (i.e., the hyperglass user) at the base.
  g.setNode(base.asn, { width: NODE_WIDTH, height: NODE_HEIGHT });

  for (const [groupIdx, pathGroup] of asPaths.entries()) {
    // For each ROUTE's AS Path:

    // Find the route after this one.
    const nextGroup = groupIdx < totalPaths ? asPaths[groupIdx + 1] : [];

    // Connect the first hop in the AS Path to the base (for dagre).
    g.setEdge(base.asn, `${groupIdx}-${pathGroup[0]}`);

    // Eliminate duplicate AS Paths.
    if (!isEqual(pathGroup, nextGroup)) {
      for (const [idx, asn] of pathGroup.entries()) {
        // For each ASN in the ROUTE:

        const node = `${groupIdx}-${asn}`;
        const endIdx = pathGroup.length - 1;

        // Add the AS as a node.
        g.setNode(node, { width: NODE_WIDTH, height: NODE_HEIGHT });

        // Connect the first hop in the AS Path to the base (for react-flow).
        if (idx === 0) {
          yield {
            id: `e${base.asn}-${node}`,
            source: base.asn,
            target: node,
          };
        }
        // Connect every intermediate hop to each other.
        if (idx !== endIdx) {
          const next = `${groupIdx}-${pathGroup[idx + 1]}`;
          g.setEdge(node, next);
          yield {
            id: `e${node}-${next}`,
            source: node,
            target: next,
          };
        }
      }
    }
  }

  // Now that that nodes are added, create the layout.
  dagre.layout(g, { rankdir: 'BT', align: 'UR' });

  // Get the base ASN's positions.
  const x = g.node(base.asn).x - NODE_WIDTH / 2;
  const y = g.node(base.asn).y + NODE_HEIGHT * 6;

  yield {
    id: base.asn,
    type: 'ASNode',
    position: { x, y },
    data: { 
      asn: base.asn, 
      name: asnOrgs[base.asn]?.name || base.name, 
      hasChildren: true, 
      hasParents: false 
    },
  };

  for (const [groupIdx, pathGroup] of asPaths.entries()) {
    const nextGroup = groupIdx < totalPaths ? asPaths[groupIdx + 1] : [];
    if (!isEqual(pathGroup, nextGroup)) {
      for (const [idx, asn] of pathGroup.entries()) {
        const node = `${groupIdx}-${asn}`;
        const endIdx = pathGroup.length - 1;
        const x = g.node(node).x - NODE_WIDTH / 2;
        const y = g.node(node).y - NODE_HEIGHT * (idx * 6);

        // Get each ASN's positions.
        yield {
          id: node,
          type: 'ASNode',
          position: { x, y },
          data: {
            asn: `${asn}`,
            name: asn === 'IXP' ? 'IXP' : asnOrgs[asn]?.name || (asn === '0' ? 'Private/Unknown' : `AS${asn}`),
            hasChildren: idx < endIdx,
            hasParents: true,
          },
        };
      }
    }
  }
}
