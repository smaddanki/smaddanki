import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://smaddanki.com"),
  title: "Sudhamshu Addanki",
  description:
    "Data engineering, machine learning, and quantitative research — notes, code, and analyses.",
  openGraph: {
    title: "Sudhamshu Addanki",
    description:
      "Data engineering, machine learning, and quantitative research — notes, code, and analyses.",
    url: "https://smaddanki.com",
    siteName: "smaddanki.com",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
