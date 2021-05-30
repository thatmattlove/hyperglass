import React from "react";
import clsx from "clsx";
import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";
import useBaseUrl from "@docusaurus/useBaseUrl";
import styles from "./styles.module.css";

function Home() {
  return (
    <Layout
      description="hyperglass is the network looking glass that tries to make the internet better."
      keywords={[
        "hyperglass",
        "documentation",
        "docs",
        "bgp",
        "lg",
        "looking",
        "glass",
        "looking glass",
        "ping",
        "traceroute",
        "matt love",
        "python",
        "python3",
        "react",
        "reactjs",
      ]}
    >
      <header className={clsx("hero", styles.heroBanner)}>
        <div className="container">
          <h1 className={clsx("hero__title", styles.title)}>hyperglass</h1>
          <h2 className={clsx("hero__subtitle", styles.subTitle)}>
            the <span className={styles.tagPrimary}>network looking glass</span>{" "}
            that tries to
            <span className={styles.tagSecondary}>
              {" "}
              make the internet better
            </span>
            .
          </h2>
          <div className={styles.buttons}>
            <Link
              className={clsx(
                "button button--outline button--secondary button--lg",
                styles.homeBtn,
                styles.btnSecondary
              )}
              to={useBaseUrl("docs/getting-started")}
            >
              Set up your Looking Glass
            </Link>
            <Link
              className={clsx(
                "button button--outline button--primary button--lg",
                styles.homeBtn,
                styles.btnPrimary
              )}
              to={useBaseUrl("docs/introduction")}
            >
              Why hyperglass?
            </Link>
          </div>
        </div>
      </header>
      <main>
        <section className={styles.content}>
          <div className="container">
            <div className="row">
              <div className={clsx("col col--4")}>
                <section className={styles.content}>
                  <div className="container">
                    <div className="row">
                      <div className={clsx("col col--12")}></div>
                    </div>
                  </div>
                </section>
              </div>
              <div className={clsx("col col--8")}></div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}

export default Home;
