import { useQuery } from '@tanstack/react-query';

import type {
  QueryFunctionContext,
  QueryObserverResult,
  QueryFunction,
} from '@tanstack/react-query';

interface ASNQuery {
  data: {
    asn: {
      organization: {
        orgName: string;
      } | null;
    };
  };
}

const query: QueryFunction<ASNQuery, string[]> = async (ctx: QueryFunctionContext) => {
  const asn = ctx.queryKey;
  const res = await fetch('https://api.asrank.caida.org/v2/graphql', {
    mode: 'cors',
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    /* eslint no-useless-escape: 0 */
    body: JSON.stringify({ query: `{ asn(asn:\"${asn}\"){ organization { orgName } } }` }),
  });
  return await res.json();
};

/**
 * Query the Caida AS Rank API to get an ASN's organization name for the AS Path component.
 * @see https://api.asrank.caida.org/v2/docs
 */
export function useASNDetail(asn: string): QueryObserverResult<ASNQuery> {
  return useQuery<ASNQuery, unknown, ASNQuery, string[]>({
    queryKey: [asn],
    queryFn: query,
    refetchOnWindowFocus: false,
    refetchInterval: false,
    refetchOnMount: false,
    cacheTime: Infinity,
  });
}
