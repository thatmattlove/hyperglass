import * as React from "react";
import classnames from "classnames";
import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";
import useBaseUrl from "@docusaurus/useBaseUrl";
import styles from "./styles.module.css";

function Screenshots() {
  return (
    <Layout
      description="hyperglass screenshots"
      keywords={["hyperglass", "screenshots"]}
    >
      <header className={classnames("hero", styles.heroBanner)}>
        <div className={classnames("container", styles.smallerTitleContainer)}>
          <h1 className={classnames("hero__title", styles.title)}>
            Coming Soon!
          </h1>
          <h2
            className={classnames(
              "hero__subtitle",
              styles.subTitle,
              styles.smallerTitle
            )}
          >
            <span className={styles.tagPrimary}>hyperglass 1.0</span> is still
            in progress, so screenshots may not be made available until shortly
            before the release.
          </h2>
          <div className={styles.buttons}>
            <Link
              className={classnames(
                "button button--outline button--secondary button--lg",
                styles.homeBtn,
                styles.btnSecondary
              )}
              to={useBaseUrl("docs/getting-started")}
            >
              Back to the Docs
            </Link>
          </div>
        </div>
      </header>
      <main>
        <section className={styles.content}>
          <div className="container">
            <div className="row">
              <div className={classnames("col col--4")}>
                <section className={styles.content}>
                  <div className="container">
                    <div className="row">
                      <div className={classnames("col col--12")}></div>
                    </div>
                  </div>
                </section>
              </div>
              <div className={classnames("col col--8")}></div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}

export default Screenshots;
