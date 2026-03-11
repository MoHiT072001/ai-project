import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terraform AI Infrastructure Analyzer",
  description: "AI-powered Terraform infrastructure code reviewer"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-zinc-800">
            <div className="mx-auto max-w-5xl px-4 py-4">
              <div className="text-lg font-semibold">
                Terraform AI Infrastructure Analyzer
              </div>
              <div className="text-sm text-zinc-400">
                Static validation • Policy enforcement • Graph analysis • AI reasoning •
                Cost optimization
              </div>
            </div>
          </header>
          <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}

