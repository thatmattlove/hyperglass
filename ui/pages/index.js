import React from "react";
import dynamic from "next/dynamic";
import Loading from "~/components/Loading";
const Layout = dynamic(() => import("~/components/Layout"), { loading: Loading });

const Index = () => <Layout />;

export default Index;
