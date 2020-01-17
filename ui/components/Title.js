import React from "react";
import { Button, Flex, Heading, Image, Stack, useColorMode } from "@chakra-ui/core";

const TitleOnly = ({ text }) => (
    <Heading as="h1" size="2xl">
        {text}
    </Heading>
);

const SubtitleOnly = ({ text }) => (
    <Heading as="h3" size="md">
        {text}
    </Heading>
);

const TextOnly = ({ text }) => (
    <Stack spacing={2}>
        <TitleOnly text={text.title} />
        <SubtitleOnly text={text.subtitle} />
    </Stack>
);

const LogoOnly = ({ text, logo }) => {
    const { colorMode } = useColorMode();
    const logoColor = { light: logo.dark, dark: logo.light };
    const logoPath = logoColor[colorMode];
    return (
        <Image
            src={`http://localhost:8001${logoPath}`}
            alt={text.title}
            w={logo.width}
            h={logo.height || null}
        />
    );
};

const LogoTitle = ({ text, logo }) => (
    <>
        <LogoOnly text={text} logo={logo} />
        <SubtitleOnly text={text.title} />
    </>
);

const All = ({ text, logo }) => (
    <>
        <LogoOnly text={text} logo={logo} />
        <TextOnly text={text} />
    </>
);

const modeMap = { text_only: TextOnly, logo_only: LogoOnly, logo_title: LogoTitle, all: All };

export default React.forwardRef(({ text, logo, resetForm }, ref) => {
    const MatchedMode = modeMap[text.title_mode];
    return (
        <Button variant="link" onClick={resetForm} _focus={{ boxShadow: "non" }}>
            <Flex ref={ref}>
                <MatchedMode text={text} logo={logo} />
            </Flex>
        </Button>
    );
});
