import * as React from "react";
import { createElement } from "react";
import Head from "next/head";
import dynamic from "next/dynamic";
import fs from "fs";
import { Parser } from "html-to-react";
import Meta from "~/components/Meta";
import Loading from "~/components/Loading";
const LookingGlass = dynamic(() => import("~/components/LookingGlass"), {
  loading: Loading
});

const Index = ({ faviconComponents }) => {
  return (
    <>
      <Head>
        {faviconComponents.map((comp, i) =>
          createElement(comp.type, { key: i, ...comp.props })
        )}
      </Head>
      <Meta />
      <LookingGlass />
    </>
  );
};

export async function getStaticProps(context) {
  const htmlToReact = new Parser();
  const lines = fs.readFileSync(process.env._FAVICON_HTML_FILE_, "utf-8");
  const components = JSON.parse(lines).map(elem => {
    const comp = htmlToReact.parse(elem);
    return { type: comp.type, props: comp.props };
  });
  return {
    props: {
      faviconComponents: components
    }
  };
}

export default Index;
