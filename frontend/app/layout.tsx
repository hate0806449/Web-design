import "./globals.css";

export const metadata = {
  title: "IG Reel Tracker",
  description: "追蹤 IG Reel 數據",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-TW">
      <body>{children}</body>
    </html>
  );
}
