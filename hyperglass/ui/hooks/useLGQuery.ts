import { useQuery } from 'react-query';
import { useConfig } from '~/context';

import type { TFormQuery } from '~/types';
import type { TUseLGQueryFn } from './types';

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

export function useLGQuery(query: TFormQuery) {
  const { request_timeout, cache } = useConfig();
  const controller = new AbortController();

  async function runQuery(ctx: TUseLGQueryFn): Promise<TQueryResponse> {
    const [url, data] = ctx.queryKey;
    const { queryLocation, queryTarget, queryType, queryVrf } = data;
    const res = await fetchWithTimeout(
      url,
      {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          query_location: queryLocation,
          query_target: queryTarget,
          query_type: queryType,
          query_vrf: queryVrf,
        }),
        mode: 'cors',
      },
      request_timeout * 1000,
      controller,
    );
    return await res.json();
  }
  return useQuery<TQueryResponse, Response | TQueryResponse | Error>(
    ['/api/query/', query],
    runQuery,
    {
      cacheTime: cache.timeout * 1000 * 0.95,
      refetchOnWindowFocus: false,
      refetchInterval: false,
      refetchOnMount: false,
    },
  );
}
