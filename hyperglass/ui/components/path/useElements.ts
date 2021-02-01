import dagre from 'dagre';
import { useMemo } from 'react';
import isEqual from 'react-fast-compare';

import type { FlowElement } from 'react-flow-renderer';
import type { BasePath } from './types';

const NODE_WIDTH = 200;
const NODE_HEIGHT = 48;

export function useElements(base: BasePath, data: TStructuredResponse): FlowElement[] {
  return useMemo(() => {
    return [...buildElements(base, data)];
  }, [data.routes.length]);
}

/**
 * Calculate the positions for each AS Path.
 * @see https://github.com/MrBlenny/react-flow-chart/issues/61
 */
function* buildElements(base: BasePath, data: TStructuredResponse): Generator<FlowElement> {
  const { routes } = data;
  // Eliminate empty AS paths & deduplicate non-empty AS paths. Length should be same as count minus empty paths.
  const asPaths = routes.filter(r => r.as_path.length !== 0).map(r => [...new Set(r.as_path)]);

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
    data: { asn: base.asn, name: base.name, hasChildren: true, hasParents: false },
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
            asn,
            name: `AS${asn}`,
            hasChildren: idx < endIdx,
            hasParents: true,
          },
        };
      }
    }
  }
}
