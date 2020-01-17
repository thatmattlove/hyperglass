import { useMemo } from "react";
import config from "~/frontend.json";

export default () => useMemo(() => config);

export const useConfig = cfg => useMemo(() => cfg);
