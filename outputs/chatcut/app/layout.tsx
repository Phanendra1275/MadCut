import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MadCut — AI Caption Studio",
  description: "Turn your voice into captions the way you chat. Telugu, natural Tenglish, English, Hindi, and Hinglish video captions.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
