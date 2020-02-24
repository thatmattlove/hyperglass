import { useMemo } from "react";

export default (mode = "light", light = "black", dark = "white") =>
    useMemo(() => (mode ? light : dark));
