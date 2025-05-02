type ColorProps = {
    hex: string;
    noText?: boolean;
};

export const Color = (props: ColorProps) => {
    const { hex, noText = false } = props;
    return (
        <span className="color-swatch-container">
            <span className={["nx-rounded-sm", "color-swatch"].join(" ")} />
            <code>{noText ? "" : hex}</code>
            <style jsx>{`
                span.color-swatch-container {
                    display: inline-flex;
                    align-items: ${noText ? "flex-end" : "center"};
                    justify-content: space-between;
                }
                span.color-swatch {
                    display: inline-flex;
                    background-color: ${hex};
                    height: 1.5rem;
                    width: 1.5rem;
                    padding: 0.5rem 0.5rem;
                    margin-right: ${noText ? "unset" : "0.5rem"};
                }
            `}</style>
        </span>
    );
};
