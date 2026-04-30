import type { Metadata } from "next";
import { Providers } from "@/components/providers";
import { STORAGE_KEYS, DATA_ATTRIBUTES } from "@/lib/constants";
import "./globals.css";

export const metadata: Metadata = {
  title: "DLO - Data Lineage Orchestrator",
  description: "A modern data lineage and transformation orchestrator",
  icons: {
    icon: "/assets/favicon.svg",
  },
};

// Inline script to prevent flash of wrong theme/sidebar state on page load
// Uses constants injected at build time for consistency
const initScript = `
(function() {
  try {
    // Theme handling
    var storedTheme = localStorage.getItem('${STORAGE_KEYS.THEME}');
    var theme = storedTheme || 'system';
    var resolved = theme === 'system'
      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : theme;
    document.documentElement.classList.add(resolved);

    // Sidebar state handling
    var sidebarCollapsed = localStorage.getItem('${STORAGE_KEYS.SIDEBAR_COLLAPSED}') === 'true';
    if (sidebarCollapsed) {
      document.documentElement.setAttribute('${DATA_ATTRIBUTES.SIDEBAR_COLLAPSED}', 'true');
    }
  } catch (e) {}
})();
`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: initScript }} />
      </head>
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
