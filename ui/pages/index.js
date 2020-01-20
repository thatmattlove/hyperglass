import React from "react";
import Layout from "~/components/Layout";

// const Index = () => {
//     // const [{ data, loading, error }, refetch] = useAxios({
//     //     url: "/config",
//     //     method: "get"
//     // });
//     // const data = undefined;
//     // const loading = false;
//     // const error = { message: "Shit broke" };
//     // const refetch = () => alert("refetched");
//     const userTheme = data && makeTheme(data.branding);
//     const theme = data ? userTheme : defaultTheme;
//     const Component = data ? <Layout /> : <PreConfig />;
//     return (
//         <ThemeProvider theme={theme}>
//             <ColorModeProvider>
//                 <CSSReset />
//                 <MediaProvider theme={theme}>
//                     <ConfigProvider>
//                         <Component />
//                     </ConfigProvider>
//                 </MediaProvider>
//             </ColorModeProvider>
//         </ThemeProvider>
//     );
// };

// Index.displayName = "Hyperglass";

const Index = () => <Layout />;

export default Index;
