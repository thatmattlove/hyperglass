/**
 * DNS Over HTTPS Types, primarily adapted from:
 *
 * @see https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
 * @see https://developers.cloudflare.com/1.1.1.1/dns-over-https/json-format
 * @see https://developers.google.com/speed/public-dns/docs/doh/json
 */
export namespace DnsOverHttps {
  /**
   * DNS RCODEs
   * @see https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml#dns-parameters-6
   */
  export enum Status {
    /**
     * No Error
     */
    NO_ERROR = 0,
    /**
     * Format Error
     */
    FORM_ERR = 1,
    /**
     * Server Failure
     */
    SERV_FAIL = 2,
    /**
     * Non-Existent Domain
     */
    NX_DOMAIN = 3,
    /**
     * 	Not Implemented
     */
    NOT_IMP = 4,
    /**
     * 	Query Refused
     */
    REFUSED = 5,
    /**
     * Name Exists when it should not
     */
    YX_DOMAIN = 6,
    /**
     * RR Set Exists when it should not
     */
    YXRR_SET = 7,
    /**
     * RR Set that should exist does not
     */
    NXRR_SET = 8,
    /**
     * Server Not Authoritative for zone
     */
    NOT_AUTH = 9,
    /**
     * Name not contained in zone
     */
    NOT_ZONE = 10,
    /**
     * DSO-TYPE Not Implemented
     */
    DSO_TYPE_NI = 11,
    /**
     * TSIG Signature Failure
     */
    BADSIG = 16,
    /**
     * Key not recognized
     */
    BADKEY = 17,
    /**
     * Signature out of time window
     */
    BADTIME = 18,
    /**
     * Bad TKEY Mode
     */
    BADMODE = 19,
    /**
     * Duplicate key name
     */
    BADNAME = 20,
    /**
     * 	Algorithm not supported
     */
    BADALG = 21,
    /**
     * Bad Truncation
     */
    BADTRUNC = 22,
    /**
     * Bad/missing Server Cookie
     */
    BADCOOKIE = 23,
  }
  /**
   * Resource Record (RR) Types
   * @see https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml#dns-parameters-4
   */
  export enum Type {
    /**
     * IPv4 Host Address Record.
     */
    A = 1,
    /**
     * Name Server Record.
     */
    NS = 2,
    /**
     * Canonical Alias Name Record.
     */
    CNAME = 5,
    /**
     * Start of Zone Authority Record.
     */
    SOA = 6,
    /**
     * Well Know Service Description Record.
     */
    WKS = 11,
    /**
     * Domain Name Pointer Record.
     */
    PTR = 12,
    /**
     * Mail Exchange Record.
     */
    MX = 15,
    /**
     * IPv6 Host Address Record.
     */
    AAAA = 28,
    /**
     * Server Selection Record.
     */
    SRV = 33,
    /**
     * DNAME Record.
     */
    DNAME = 39,
    /**
     * DNSKEY Record.
     */
    DNSKEY = 48,
  }
  export interface Question {
    /**
     * FQDN with trailing dot.
     */
    name: string;
    /**
     * DNS RR Type.
     */
    type: Type;
  }
  export interface Answer {
    /**
     * FQDN with trailing dot.
     */
    name: string;
    /**
     * DNS RR Type.
     */
    type: Type;
    /**
     * Time to live in seconds.
     */
    TTL: number;
    /**
     * Response data.
     */
    data: string;
  }
  export interface Response {
    Status: Status;
    /**
     * Truncated bit was set.
     */
    TC: boolean;
    /**
     * Recursive Desired bit was set.
     */
    RD: boolean;
    /**
     * Recursion Available bit was set.
     */
    RA: boolean;
    /**
     * If true, it means that every record in the answer was verified with DNSSEC.
     */
    AD: boolean;
    /**
     * If true, the client asked to disable DNSSEC validation.
     */
    CD: boolean;
    /**
     * Queried Resources.
     */
    Question: Question[];
    /**
     * Response Data.
     */
    Answer: Answer[];
  }
}
