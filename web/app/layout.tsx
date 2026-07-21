import type { Metadata } from "next";
import "./globals.css";

const url = "https://prompt-lab.kareemghazal.com";
const title = "prompt-lab — measure a prompt, don't vibe it";
const description =
  "Paste a prompt and a few test cases; it runs the prompt, an independent judge scores pass/fail per case, and you get a pass-rate, the failure pattern, and a suggested better prompt. A tiny eval harness as a product.";

export const metadata: Metadata = {
  metadataBase: new URL(url),
  title,
  description,
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    url,
    siteName: "prompt-lab",
    title,
    description,
    locale: "en_GB",
    images: [{ url: "/og.jpg", width: 1200, height: 630, alt: "prompt-lab — a prompt evaluation harness" }],
  },
  twitter: { card: "summary_large_image", title, description, images: ["/og.jpg"] },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
