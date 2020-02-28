import React from "react";
import classnames from "classnames";
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
                "bgp",
                "lg",
                "looking",
                "glass",
                "ping",
                "traceroute",
                "test"
            ]}
        >
            <header className={classnames("hero", styles.heroBanner)}>
                <div className="container">
                    <h1 className={classnames("hero__title", styles.title)}>hyperglass</h1>
                    <h3 className={classnames("hero__subtitle", styles.subTitle)}>
                        the <span className={styles.tag}>network looking glass</span> that tries to
                        make the internet better.
                    </h3>
                    <div className={styles.buttons}>
                        <Link
                            className={classnames(
                                "button button--outline button--secondary button--lg",
                                styles.getStarted
                            )}
                            to={useBaseUrl("docs/getting-started")}
                        >
                            Get Started
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

export default Home;
