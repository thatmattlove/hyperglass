import React from "react";
import Code from "./JSXCode";

const patternMap = {
    aspath_asdot: String.raw`^(\^|^\_)((\d+\.\d+)\_|(\d+\.\d+)\$|(\d+\.\d+)\(\_\.\+\_\))+$`,
    aspath_asplain: String.raw`^(\^|^\_)(\d+\_|\d+\$|\d+\(\_\.\+\_\))+$`,
    community_decimal: String.raw`^[0-9]{1,10}$`,
    community_extended: String.raw`^([0-9]{0,5})\:([0-9]{1,5})$`,
    community_large: String.raw`^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$`
};

export default ({ pattern }) => {
    const thisPattern = patternMap[pattern];
    return <Code>'{thisPattern}'</Code>;
};
