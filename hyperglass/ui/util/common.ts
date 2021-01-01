export function all(...iter: any[]) {
  for (let i of iter) {
    if (!i) {
      return false;
    }
  }
  return true;
}

export function flatten<T extends unknown>(arr: any[][]): T[] {
  return arr.reduce(function (flat, toFlatten) {
    return flat.concat(Array.isArray(toFlatten) ? flatten(toFlatten) : toFlatten);
  }, []);
}

export function chunkArray<A extends any>(array: A[], size: number): A[][] {
  let result = [] as A[][];
  for (let i = 0; i < array.length; i += size) {
    let chunk = array.slice(i, i + size);
    result.push(chunk);
  }
  return result;
}

interface PathPart {
  base: number;
  children: PathPart[];
}

/**
 * Arrange an array of arrays into a tree of nodes.
 *
 * Blatantly stolen from:
 * @see https://gist.github.com/stephanbogner/4b590f992ead470658a5ebf09167b03d
 */
export function arrangeIntoTree<P extends any>(paths: P[][]): PathPart[] {
  let tree = [] as PathPart[];

  for (let i = 0; i < paths.length; i++) {
    let path = paths[i];
    let currentLevel = tree;

    for (let j = 0; j < path.length; j++) {
      let part = path[j];

      const existingPath = findWhere(currentLevel, 'base', part);

      if (existingPath !== false) {
        currentLevel = existingPath.children;
      } else {
        const newPart = {
          base: part,
          children: [],
        } as PathPart;

        currentLevel.push(newPart);
        currentLevel = newPart.children;
      }
    }
  }
  return tree;

  function findWhere<V extends any>(array: any[], idx: string, value: V): PathPart | false {
    let t = 0;
    while (t < array.length && array[t][idx] !== value) {
      t++;
    }

    if (t < array.length) {
      return array[t];
    } else {
      return false;
    }
  }
}

/**
 * Fetch Wrapper that incorporates a timeout via a passed AbortController instance.
 *
 * Adapted from: https://lowmess.com/blog/fetch-with-timeout
 */
export async function fetchWithTimeout(
  uri: string,
  options: RequestInit = {},
  timeout: number,
  controller: AbortController,
): Promise<Response> {
  /**
   * Lets set up our `AbortController`, and create a request options object that includes the
   * controller's `signal` to pass to `fetch`.
   */
  const { signal = new AbortController().signal, ...allOptions } = options;
  const config = { ...allOptions, signal };
  /**
   * Set a timeout limit for the request using `setTimeout`. If the body of this timeout is
   * reached before the request is completed, it will be cancelled.
   */
  setTimeout(() => {
    controller.abort();
  }, timeout);
  return await fetch(uri, config);
}
