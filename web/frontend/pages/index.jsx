import { Page, Layout } from "@shopify/polaris";
import { TitleBar } from "@shopify/app-bridge-react";
import { useTranslation } from "react-i18next";

import { tree } from "../assets";

export default function HomePage() {
    const { t } = useTranslation();
    return (
        <Page narrowWidth>
            <TitleBar title={"Django Boiler Plate"} primaryAction={null} />
            <Layout>
                <Layout.Section>
                    <img src={tree} width={100} height={100} />
                </Layout.Section>
            </Layout>
        </Page>
    );
}
