import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Paper Trading",
  description: "AI-powered paper trading platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-light">{children}</body>
    </html>
  );
}
