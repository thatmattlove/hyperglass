import React from "react";
import { Button, Heading, Image, Stack, useColorMode } from "@chakra-ui/core";
import { Textfit } from "react-textfit";
import { motion, AnimatePresence } from "framer-motion";
import useConfig from "~/components/HyperglassProvider";
import useMedia from "~/components/MediaProvider";

const subtitleAnimation = {
    transition: { duration: 0.2, type: "tween" },
    initial: { opacity: 1, scale: 1 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.3 }
};

const titleSize = { true: "2xl", false: "lg" };
const titleMargin = { true: 2, false: 0 };

const TitleOnly = ({ text, showSubtitle }) => (
    <Heading as="h1" mb={titleMargin[showSubtitle]} size={titleSize[showSubtitle]}>
        <Textfit mode="single">{text}</Textfit>
    </Heading>
);

const SubtitleOnly = React.forwardRef(({ text, size = "md", ...props }, ref) => (
    <Heading ref={ref} as="h3" size={size} {...props}>
        <Textfit mode="single" max={20}>
            {text}
        </Textfit>
    </Heading>
));

const AnimatedSubtitle = motion.custom(SubtitleOnly);

const textAlignment = { false: ["right", "center"], true: ["left", "center"] };

const TextOnly = ({ text, mediaSize, showSubtitle, ...props }) => (
    <Stack spacing={2} maxW="100%" textAlign={textAlignment[showSubtitle]} {...props}>
        <TitleOnly text={text.title} showSubtitle={showSubtitle} />
        <AnimatePresence>
            {showSubtitle && <AnimatedSubtitle text={text.subtitle} {...subtitleAnimation} />}
        </AnimatePresence>
    </Stack>
);

const Logo = ({ text, logo }) => {
    const { colorMode } = useColorMode();
    const logoColor = { light: logo.dark, dark: logo.light };
    const logoPath = logoColor[colorMode];
    return <Image src={logoPath} alt={text.title} />;
};

const LogoTitle = ({ text, logo, showSubtitle }) => (
    <>
        <Logo text={text} logo={logo} />
        <AnimatePresence>
            {showSubtitle && (
                <AnimatedSubtitle mt={2} text={text.subtitle} {...subtitleAnimation} />
            )}
        </AnimatePresence>
    </>
);

const All = ({ text, logo, mediaSize, showSubtitle }) => (
    <>
        <Logo text={text} logo={logo} />
        <TextOnly mediaSize={mediaSize} showSubtitle={showSubtitle} mt={2} text={text} />
    </>
);

const modeMap = { text_only: TextOnly, logo_only: Logo, logo_title: LogoTitle, all: All };

const btnJustify = {
    true: ["flex-end", "center"],
    false: ["flex-start", "center"]
};
export default React.forwardRef(({ onClick, isSubmitting, ...props }, ref) => {
    const { web } = useConfig();
    const { mediaSize } = useMedia();
    const titleMode = web.text.title_mode;
    const MatchedMode = modeMap[titleMode];
    return (
        <Button
            ref={ref}
            variant="link"
            onClick={onClick}
            flexWrap="wrap"
            _focus={{ boxShadow: "none" }}
            _hover={{ textDecoration: "none" }}
            justifyContent={btnJustify[isSubmitting]}
            px={0}
            maxW="100%"
            {...props}
        >
            <MatchedMode
                mediaSize={mediaSize}
                showSubtitle={!isSubmitting}
                text={web.text}
                logo={web.logo}
            />
        </Button>
    );
});
