"use client";

import type { ReactNode } from "react";
import { QueryProvider } from "./QueryProvider";
import { ThemeProvider } from "@/components/layout/ThemeProvider";
import { ManifestProvider } from "@/hooks/use-manifest";

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <QueryProvider>
      <ThemeProvider defaultTheme="light" storageKey="dlo-ui-theme">
        <ManifestProvider>{children}</ManifestProvider>
      </ThemeProvider>
    </QueryProvider>
  );
}
