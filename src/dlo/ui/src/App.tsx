import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout, ThemeProvider } from '@/components/layout';
import { ManifestProvider } from '@/context';
import {
  Dashboard,
  Sources,
  Models,
  Relationships,
  Metrics,
  Lineage,
  Search,
  SourceDetail,
  ModelDetail,
  RelationshipDetail,
  MetricDetail,
} from '@/pages';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light" storageKey="dlo-ui-theme">
        <ManifestProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Layout />}>
                <Route index element={<Dashboard />} />
                <Route path="sources" element={<Sources />} />
                <Route path="sources/:name" element={<SourceDetail />} />
                <Route path="models" element={<Models />} />
                <Route path="models/:name" element={<ModelDetail />} />
                <Route path="relationships" element={<Relationships />} />
                <Route path="relationships/:name" element={<RelationshipDetail />} />
                <Route path="metrics" element={<Metrics />} />
                <Route path="metrics/:name" element={<MetricDetail />} />
                <Route path="lineage" element={<Lineage />} />
                <Route path="search" element={<Search />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </ManifestProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
