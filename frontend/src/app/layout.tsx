import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "PM Internship Engine - AI-Based Smart Allocation",
  description:
    "AI-Based Smart Allocation Engine for PM Internship Scheme - Connecting candidates with opportunities through intelligent matching",
  keywords: ["PM Internship", "allocation engine", "AI matching", "government internship"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background text-foreground antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
