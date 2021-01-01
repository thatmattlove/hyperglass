export interface TASNQuery {
  data: {
    asn: {
      organization: {
        orgName: string;
      } | null;
    };
  };
}
