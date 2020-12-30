import { useQuery } from 'react-query';
import { useConfig } from '~/context';
import { fetchWithTimeout } from '~/util';

import type { TFormQuery } from '~/types';
import type { TUseLGQueryFn } from './types';

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
