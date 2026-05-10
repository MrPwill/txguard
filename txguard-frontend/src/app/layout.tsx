import type { Metadata } from "next";
import { Syne, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import Providers from "./providers";

const syne = Syne({ subsets: ["latin"], variable: "--font-display" });
const plexMono = IBM_Plex_Mono({ weight: ["400", "500", "600"], subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "TxGuard AI",
  description: "Intelligent Transaction Monitoring & Fraud Investigation System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${syne.variable} ${plexMono.variable}`}>
      <body className="bg-bg text-text antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
