import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useUIStore } from '@/store/uiStore';
import { useAuthStore } from '@/store/authStore';
import {
  Brain,
  Database,
  BarChart3,
  Users,
  Shield,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  LayoutDashboard,
  Server,
} from 'lucide-react';

const navItems = [
  { icon: Brain, label: 'Query Console', path: '/dashboard/query' },
  { icon: Database, label: 'Data Manager', path: '/dashboard/data' },
  { icon: BarChart3, label: 'Analytics', path: '/dashboard/analytics' },
  { icon: Users, label: 'Users', path: '/dashboard/users', roles: ['admin', 'super_admin'] },
  { icon: Shield, label: 'Audit Logs', path: '/dashboard/audit', roles: ['admin', 'super_admin'] },
  { icon: Server, label: 'Connections', path: '/dashboard/connections' },
  { icon: Settings, label: 'Settings', path: '/dashboard/settings' },
];

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const location = useLocation();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const visibleItems = navItems.filter(
    (item) => !item.roles || (user?.role && item.roles.includes(user.role))
  );

  return (
    <aside
      className={`fixed left-0 top-0 z-40 flex h-screen flex-col border-r border-border bg-sidebar transition-all duration-300 ${
        sidebarCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-border px-4">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg animated-gradient">
          <LayoutDashboard className="h-4 w-4 text-white" />
        </div>
        {!sidebarCollapsed && (
          <span className="text-sm font-bold gradient-text truncate">
            AI Data Platform
          </span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-2 py-4">
        {visibleItems.map(({ icon: Icon, label, path }) => {
          const active = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={`group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
                active
                  ? 'bg-primary/15 text-primary glow-primary'
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground'
              }`}
            >
              <Icon className={`h-5 w-5 shrink-0 ${active ? 'text-primary' : ''}`} />
              {!sidebarCollapsed && <span className="truncate">{label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* User / Collapse */}
      <div className="border-t border-border p-2">
        <button
          onClick={() => logout()}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
        >
          <LogOut className="h-5 w-5 shrink-0" />
          {!sidebarCollapsed && <span>Logout</span>}
        </button>
        <button
          onClick={toggleSidebar}
          className="flex w-full items-center justify-center rounded-lg py-2 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground mt-1"
        >
          {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>
    </aside>
  );
}
