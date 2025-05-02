import { Code, Table, Td, Th, Tr } from "nextra/components";
import platforms from "~/platforms.json";
import { NotSupported } from "./not-supported-icon";
import { Supported } from "./supported-icon";

export const SupportedPlatforms = () => (
    <ul className="nx-mt-2 first:nx-mt-0 ltr:nx-ml-6 rtl:nx-mr-6">
        {platforms.reduce<React.ReactNode[]>((final, platform) => {
            if (platform.native) {
                const element = (
                    <li key={platform.name}>
                        <Supported style={{ display: "inline", marginRight: "0.5rem" }} />
                        {platform.name}
                    </li>
                );
                final.push(element);
            }
            return final;
        }, [])}
    </ul>
);

export const PlatformTable = () => (
    <Table>
        <tbody>
            <Tr>
                <Th>Platform Keys</Th>
                <Th>Natively Supported</Th>
            </Tr>
            {platforms.map((spec) => (
                <Tr key={spec.keys.join("--")}>
                    <Td>
                        {spec.keys.map((key) => (
                            <Code className="nx-mx-2" key={key}>
                                {key}
                            </Code>
                        ))}
                    </Td>
                    <Td align="center">{spec.native ? <Supported /> : <NotSupported />}</Td>
                </Tr>
            ))}
        </tbody>
    </Table>
);
