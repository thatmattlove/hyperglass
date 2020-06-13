import * as React from "react";
import dynamic from "next/dynamic";
import Meta from "~/components/Meta";
import Loading from "~/components/Loading";
const LookingGlass = dynamic(() => import("~/components/LookingGlass"), {
  loading: Loading
});

const Index = () => (
  <>
    <Meta />
    <LookingGlass />
  </>
);

export default Index;
