import { Link, useLocation } from 'react-router-dom';
import {
  Database,
  Box,
  GitBranch,
  BarChart3,
  LayoutDashboard,
  Network,
  Search,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Sources', href: '/sources', icon: Database },
  { name: 'Models', href: '/models', icon: Box },
  { name: 'Relationships', href: '/relationships', icon: GitBranch },
  { name: 'Metrics', href: '/metrics', icon: BarChart3 },
  { name: 'Lineage', href: '/lineage', icon: Network },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <div className="flex h-full w-64 flex-col border-r border-border bg-sidebar-background">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg">
          <img src='/favicon.svg' className="h-6 w-6 text-primary-foreground" />
        </div>
        <span className="text-xl font-bold text-sidebar-foreground">DLO</span>
      </div>

      <Separator />

      {/* Search */}
      <div className="px-4 py-4">
        <Link
          to="/search"
          className={cn(
            'flex items-center gap-2 rounded-lg border border-input bg-background px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground',
            location.pathname === '/search' && 'bg-accent text-accent-foreground'
          )}
        >
          <Search className="h-4 w-4" />
          <span>Search...</span>
          <kbd className="ml-auto pointer-events-none hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
            <span className="text-xs">/</span>
          </kbd>
        </Link>
      </div>

      <Separator />

      {/* Navigation */}
      <ScrollArea className="flex-1 px-4 py-4">
        <nav className="flex flex-col gap-1">
          {navigation.map((item) => {
            const isActive = item.href === '/' 
              ? location.pathname === '/'
              : location.pathname.startsWith(item.href);
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </ScrollArea>

      {/* Footer */}
      <Separator />
      <div className="p-4">
        <div className="rounded-lg bg-muted p-3">
          <p className="text-xs text-muted-foreground">
            Data Lineage Orchestrator
          </p>
          <p className="text-xs font-medium text-foreground">v0.0.1</p>
        </div>
      </div>
    </div>
  );
}
