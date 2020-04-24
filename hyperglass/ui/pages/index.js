import * as React from "react";
import dynamic from "next/dynamic";
import Loading from "~/components/Loading";
const LookingGlass = dynamic(() => import("~/components/LookingGlass"), {
  loading: Loading
});

const Index = () => <LookingGlass />;

export default Index;
