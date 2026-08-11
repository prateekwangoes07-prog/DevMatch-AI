import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DevMatch AI - Intelligent Developer Allocation & Client Management",
  description: "Seamless match-making and automated scheduling for elite developers and industry clients.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
