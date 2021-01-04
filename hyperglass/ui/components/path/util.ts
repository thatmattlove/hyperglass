import { arrangeIntoTree } from '~/util';

import type { FlowElement, Elements } from 'react-flow-renderer';
import type { PathPart } from '~/types';
import type { BasePath } from './types';

function treeToElement(part: PathPart, len: number, index: number): FlowElement[] {
  const x = index * 250;
  const y = -(len * 10);
  const elements = [
    {
      id: String(part.base),
      type: 'ASNode',
      position: { x, y },
      data: {
        asn: part.base,
        name: `AS${part.base}`,
        hasChildren: part.children.length !== 0,
        hasParents: true,
      },
    },
  ] as Elements;

  for (const child of part.children) {
    let xc = index;
    if (part.children.length !== 0) {
      elements.push({
        id: `e${part.base}-${child.base}`,
        source: String(part.base),
        target: String(child.base),
      });
    } else {
      xc = x;
    }
    elements.push(...treeToElement(child, part.children.length * 12 + len, xc));
  }
  return elements;
}

export function* buildElements(base: BasePath, data: TStructuredResponse): Generator<FlowElement> {
  const { routes } = data;
  // Eliminate empty AS paths & deduplicate non-empty AS paths. Length should be same as count minus empty paths.
  const asPaths = routes.filter(r => r.as_path.length !== 0).map(r => [...new Set(r.as_path)]);
  const asTree = arrangeIntoTree(asPaths);
  const numHops = asPaths.flat().length;
  const childPaths = asTree.map((a, i) => {
    return treeToElement(a, asTree.length, i);
  });

  // Add the first hop at the base.
  yield {
    id: base.asn,
    type: 'ASNode',
    position: { x: 150, y: numHops * 10 },
    data: { asn: base.asn, name: base.name, hasChildren: true, hasParents: false },
  };

  for (const path of childPaths) {
    // path = Each unique path from origin
    const first = path[0];
    yield { id: `e${base.asn}-${first.id}`, source: base.asn, target: first.id };
    // Add link from base to each first hop.
    yield { id: `e${base.asn}-${first.id}`, source: base.asn, target: first.id };
    for (const hop of path) {
      yield hop;
    }
  }
}
