export function all<I extends unknown>(...iter: I[]): boolean {
  for (const i of iter) {
    if (!i) {
      return false;
    }
  }
  return true;
}

export function chunkArray<A extends unknown>(array: A[], size: number): A[][] {
  const result = [] as A[][];
  for (let i = 0; i < array.length; i += size) {
    const chunk = array.slice(i, i + size);
    result.push(chunk);
  }
  return result;
}

type PathPart = {
  base: number;
  children: PathPart[];
};

/**
 * Arrange an array of arrays into a tree of nodes.
 *
 * Blatantly stolen from:
 * @see https://gist.github.com/stephanbogner/4b590f992ead470658a5ebf09167b03d
 */
export function arrangeIntoTree<P extends unknown>(paths: P[][]): PathPart[] {
  const tree = [] as PathPart[];

  for (let i = 0; i < paths.length; i++) {
    const path = paths[i];
    let currentLevel = tree;

    for (let j = 0; j < path.length; j++) {
      const part = path[j];

      const existingPath = findWhere<PathPart, typeof part>(currentLevel, 'base', part);

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

  function findWhere<A extends Record<string, unknown>, V extends unknown>(
    array: A[],
    idx: string,
    value: V,
  ): A | false {
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
 * Strictly typed version of `Object.entries()`.
 */
export function entries<O, K extends keyof O = keyof O>(obj: O): [K, O[K]][] {
  const _entries = [] as [K, O[K]][];
  const keys = Object.keys(obj) as K[];
  for (const key of keys) {
    _entries.push([key, obj[key]]);
  }
  return _entries;
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

export function dedupObjectArray<E extends Record<string, unknown>, P extends keyof E = keyof E>(
  arr: E[],
  property: P,
): E[] {
  return arr.reduce((acc: E[], current: E) => {
    const x = acc.find(item => item[property] === current[property]);
    if (!x) {
      return acc.concat([current]);
    } else {
      return acc;
    }
  }, []);
}

interface AndJoinOptions {
  /**
   * Separator for last item.
   *
   * @default '&'
   */
  separator?: string;

  /**
   * Use the oxford comma.
   *
   * @default true
   */
  oxfordComma?: boolean;

  /**
   * Wrap each item in a character.
   *
   * @default ''
   */
  wrap?: string;
}

/**
 * Create a natural list of values from an array of strings
 * @param values
 * @param options
 * @returns
 */
export function andJoin(values: string[], options?: AndJoinOptions): string {
  let mergedOptions = { separator: '&', oxfordComma: true, wrap: '' } as Required<AndJoinOptions>;
  if (typeof options === 'object' && options !== null) {
    mergedOptions = { ...mergedOptions, ...options };
  }
  const { separator, oxfordComma, wrap } = mergedOptions;
  const parts = values.filter(v => typeof v === 'string');
  const lastElement = parts.pop();
  if (typeof lastElement === 'undefined') {
    return '';
  }
  const last = [wrap, lastElement, wrap].join('');
  if (parts.length > 0) {
    const main = parts.map(p => [wrap, p, wrap].join('')).join(', ');
    const comma = oxfordComma && parts.length > 2 ? ',' : '';
    const result = `${main}${comma} ${separator} ${last}`;
    return result.trim();
  }
  return last;
}
