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

// Disabled - we now get org names from our own IP enrichment system
// const query: QueryFunction<ASNQuery, string[]> = async (ctx: QueryFunctionContext) => {
//   const asn = ctx.queryKey;
//   const res = await fetch('https://api.asrank.caida.org/v2/graphql', {
//     mode: 'cors',
//     method: 'POST',
//     headers: { 'content-type': 'application/json' },
//     /* eslint no-useless-escape: 0 */
//     body: JSON.stringify({ query: `{ asn(asn:\"${asn}\"){ organization { orgName } } }` }),
//   });
//   return await res.json();
// };

/**
 * Stub function - we no longer need external CAIDA calls since we have ASN org data
 * from our IP enrichment system. This hook is kept for compatibility but returns empty data.
 * @deprecated Use as_path_data from traceroute response instead of external CAIDA calls
 */
export function useASNDetail(asn: string): QueryObserverResult<ASNQuery> {
  return useQuery<ASNQuery, unknown, ASNQuery, string[]>({
    queryKey: [asn],
    queryFn: async () => ({
      data: {
        asn: {
          organization: null, // No external fetch - org data comes from IP enrichment
        }
      }
    }),
    refetchOnWindowFocus: false,
    refetchInterval: false, 
    refetchOnMount: false,
    cacheTime: Infinity,
    enabled: false, // Disable the query entirely
  });
}
