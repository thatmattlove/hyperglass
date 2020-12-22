interface TASNRIRAllocation {
  rir_name: string | null;
  country_code: string | null;
  date_allocated: string | null;
}
interface TASNData {
  asn: number;
  name: string | null;
  description_short: string | null;
  description_full: string[];
  country_code: string;
  website: string | null;
  email_contacts: string[];
  abuse_contacts: string[];
  looking_glass: string | null;
  traffic_estimation: string | null;
  traffic_ratio: string | null;
  owner_address: string[];
  rir_allocation: TASNRIRAllocation;
  date_updated: string | null;
}
export interface TASNDetails {
  status: string;
  status_message: string;
  data: TASNData;
}
