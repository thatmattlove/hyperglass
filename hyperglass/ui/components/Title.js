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
    exit: { opacity: 0, scale: 0.3 },
};
const titleSize = { true: "2xl", false: "lg" };
const titleMargin = { true: 2, false: 0 };
const textAlignment = { false: ["right", "center"], true: ["left", "center"] };

const TitleOnly = ({ text, showSubtitle }) => (
    <Heading as="h1" mb={titleMargin[showSubtitle]} size={titleSize[showSubtitle]}>
        <Textfit mode="single">{text}</Textfit>
    </Heading>
);

const SubtitleOnly = React.forwardRef(({ text, mediaSize, size = "md", ...props }, ref) => (
    <Heading ref={ref} as="h3" size={size} {...props}>
        <Textfit mode="single" max={mediaSize === "sm" ? 13 : 25}>
            {text}
        </Textfit>
    </Heading>
));

const AnimatedSubtitle = motion.custom(SubtitleOnly);

const TextOnly = ({ text, mediaSize, showSubtitle, ...props }) => (
    <Stack spacing={2} maxW="100%" textAlign={textAlignment[showSubtitle]} {...props}>
        <Textfit mode="single" max={20}>
            <TitleOnly text={text.title} showSubtitle={showSubtitle} />
        </Textfit>
        <AnimatePresence>
            {showSubtitle && (
                <AnimatedSubtitle
                    text={text.subtitle}
                    mediaSize={mediaSize}
                    {...subtitleAnimation}
                />
            )}
        </AnimatePresence>
    </Stack>
);

const Logo = ({ text, logo, showSubtitle }) => {
    const { colorMode } = useColorMode();
    const logoColor = { light: logo.dark, dark: logo.light };
    const logoPath = logoColor[colorMode];
    return <Image src={logoPath} alt={text.title} width={logo.width ?? "auto"} />;
};

const LogoSubtitle = ({ text, logo, showSubtitle, mediaSize }) => (
    <>
        <Logo text={text} logo={logo} showSubtitle={showSubtitle} mediaSize={mediaSize} />
        <AnimatePresence>
            {showSubtitle && (
                <AnimatedSubtitle mt={6} text={text.subtitle} {...subtitleAnimation} />
            )}
        </AnimatePresence>
    </>
);

const All = ({ text, logo, mediaSize, showSubtitle }) => (
    <>
        <Logo text={text} logo={logo} showSubtitle={showSubtitle} />
        <TextOnly mediaSize={mediaSize} showSubtitle={showSubtitle} mt={2} text={text} />
    </>
);

const modeMap = { text_only: TextOnly, logo_only: Logo, logo_subtitle: LogoSubtitle, all: All };
const justifyMap = {
    true: ["flex-end", "center", "center", "center"],
    false: ["flex-start", "center", "center", "center"],
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
            px={0}
            justifyContent={justifyMap[isSubmitting]}
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
