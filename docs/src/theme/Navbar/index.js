/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { useCallback, useState } from "react";
import Link from "@docusaurus/Link";
import { useLocation } from "react-router-dom";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import useBaseUrl from "@docusaurus/useBaseUrl";

import SearchBar from "@theme/SearchBar";
import Toggle from "@theme/Toggle";

import classnames from "classnames";

import useThemeContext from "@theme/hooks/useThemeContext";
import useHideableNavbar from "@theme/hooks/useHideableNavbar";
import useLockBodyScroll from "@theme/hooks/useLockBodyScroll";

import Logo from "../../components/Logo";
import styles from "./styles.module.css";

function NavLink({ to, href, label, position, ...props }) {
    const toUrl = useBaseUrl(to);
    return (
        <Link
            className={classnames(styles.navLink, "navbar__item navbar__link")}
            {...(href
                ? {
                      target: "_blank",
                      rel: "noopener noreferrer",
                      href
                  }
                : {
                      activeClassName: "navbar__link--active",
                      to: toUrl
                  })}
            {...props}
        >
            {label}
        </Link>
    );
}

function Navbar() {
    const context = useDocusaurusContext();
    const { siteConfig = {} } = context;
    const { baseUrl, themeConfig = {} } = siteConfig;
    const { navbar = {}, disableDarkMode = false } = themeConfig;
    const { title, logo = {}, links = [], hideOnScroll = false } = navbar;

    const [sidebarShown, setSidebarShown] = useState(false);
    const [isSearchBarExpanded, setIsSearchBarExpanded] = useState(false);
    const { pathname } = useLocation();

    const { isDarkTheme, setLightTheme, setDarkTheme } = useThemeContext();
    const { navbarRef, isNavbarVisible } = useHideableNavbar(hideOnScroll);

    useLockBodyScroll(sidebarShown);

    const showSidebar = useCallback(() => {
        setSidebarShown(true);
    }, [setSidebarShown]);
    const hideSidebar = useCallback(() => {
        setSidebarShown(false);
    }, [setSidebarShown]);

    const onToggleChange = useCallback(e => (e.target.checked ? setDarkTheme() : setLightTheme()), [
        setLightTheme,
        setDarkTheme
    ]);

    const logoLink = logo.href || baseUrl;
    const isExternalLogoLink = /http/.test(logoLink);
    const logoLinkProps = isExternalLogoLink
        ? {
              rel: "noopener noreferrer",
              target: "_blank"
          }
        : null;
    const logoSrc = logo.srcDark && isDarkTheme ? logo.srcDark : logo.src;
    const logoImageUrl = useBaseUrl(logoSrc);

    return (
        <nav
            ref={navbarRef}
            className={classnames("navbar", "navbar--light", "navbar--fixed-top", {
                [styles.navbarMain]: pathname === "/",
                [styles.navbarOther]: pathname !== "/",
                "navbar-sidebar--show": sidebarShown,
                [styles.navbarHideable]: hideOnScroll,
                [styles.navbarHidden]: !isNavbarVisible
            })}
        >
            <div className="navbar__inner">
                <div className={classnames("navbar__items", styles.navbarItems)}>
                    <Link className="navbar__brand" to={baseUrl}>
                        <Logo color="#fff" size={32} className={styles.logo} />
                        {title != null && (
                            <strong className={isSearchBarExpanded ? styles.hideLogoText : ""}>
                                {title}
                            </strong>
                        )}
                    </Link>
                    <div
                        aria-label="Navigation bar toggle"
                        className="navbar__toggle"
                        role="button"
                        tabIndex={0}
                        onClick={showSidebar}
                        onKeyDown={showSidebar}
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="30"
                            height="30"
                            viewBox="0 0 30 30"
                            role="img"
                            focusable="false"
                        >
                            <title>Menu</title>
                            <path
                                stroke="currentColor"
                                strokeLinecap="round"
                                strokeMiterlimit="10"
                                strokeWidth="2"
                                d="M4 7h22M4 15h22M4 23h22"
                            />
                        </svg>
                    </div>
                    {links
                        .filter(linkItem => linkItem.position !== "right")
                        .map((linkItem, i) => (
                            <NavLink {...linkItem} key={i} />
                        ))}
                </div>
                <div
                    className={classnames(
                        "navbar__items",
                        "navbar__items--right",
                        styles.navbarItemsRight
                    )}
                >
                    {!disableDarkMode && (
                        <Toggle
                            className={classnames(styles.displayOnlyInLargeViewport, styles.toggle)}
                            aria-label="Dark mode toggle"
                            checked={isDarkTheme}
                            onChange={onToggleChange}
                        />
                    )}
                    {links
                        .filter(linkItem => linkItem.position === "right")
                        .map((linkItem, i) => (
                            <NavLink {...linkItem} key={i} />
                        ))}

                    <a
                        className={classnames(
                            styles.displayOnlyInLargeViewport,
                            "button button--primary",
                            styles.button
                        )}
                        href={`https://github.com/${siteConfig.organizationName}/${siteConfig.projectName}`}
                        style={{ margin: 0, marginLeft: 15 }}
                    >
                        GITHUB →
                    </a>
                    <SearchBar
                        handleSearchBarToggle={setIsSearchBarExpanded}
                        isSearchBarExpanded={isSearchBarExpanded}
                    />
                </div>
            </div>
            <div role="presentation" className="navbar-sidebar__backdrop" onClick={hideSidebar} />
            <div className="navbar-sidebar">
                <div className="navbar-sidebar__brand">
                    <Link className="navbar__brand" onClick={hideSidebar} to={baseUrl}>
                        {logo != null && (
                            <img
                                className="navbar__logo logo--light"
                                src={logoSrc}
                                alt={logo.alt}
                            />
                        )}
                        <Logo color="#fff" size={32} className={styles.logo} />
                        {title != null && <strong>{title}</strong>}
                    </Link>
                    {!disableDarkMode && sidebarShown && (
                        <Toggle
                            aria-label="Dark mode toggle in sidebar"
                            checked={isDarkTheme}
                            onChange={onToggleChange}
                        />
                    )}
                </div>
                <div className="navbar-sidebar__items">
                    <div className="menu">
                        <ul className="menu__list">
                            {links.map((linkItem, i) => (
                                <li className="menu__list-item" key={i}>
                                    <NavLink
                                        className="menu__link"
                                        {...linkItem}
                                        onClick={hideSidebar}
                                    />
                                </li>
                            ))}

                            <div style={{ margin: 5, marginTop: 15 }}></div>
                            <a
                                className={classnames(
                                    "button button--block button--primary",
                                    styles.button
                                )}
                                href={siteConfig.url}
                            >
                                GITHUB →
                            </a>
                        </ul>
                    </div>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
