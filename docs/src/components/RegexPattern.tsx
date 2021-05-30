import * as React from "react";
import { useMemo } from "react";
import Code from "./JSXCode";

const PATTERN_MAP = {
  aspath_asdot: String.raw`^(\^|^\_)((\d+\.\d+)\_|(\d+\.\d+)\$|(\d+\.\d+)\(\_\.\+\_\))+$`,
  aspath_asplain: String.raw`^(\^|^\_)(\d+\_|\d+\$|\d+\(\_\.\+\_\))+$`,
  community_decimal: String.raw`^[0-9]{1,10}$`,
  community_extended: String.raw`^([0-9]{0,5})\:([0-9]{1,5})$`,
  community_large: String.raw`^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$`,
};

type RegexPatternProps = {
  pattern: keyof typeof PATTERN_MAP;
};

const RegexPattern = (
  props: React.PropsWithChildren<RegexPatternProps>
): JSX.Element => {
  const { pattern } = props;
  const thisPattern = useMemo<string>(() => PATTERN_MAP[pattern], [pattern]);
  return <Code>'{thisPattern}'</Code>;
};

export default RegexPattern;
