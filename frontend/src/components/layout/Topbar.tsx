import { useAuthStore } from '@/store/authStore';
import { useUIStore } from '@/store/uiStore';
import { Moon, Sun, User } from 'lucide-react';

export function Topbar() {
  const user = useAuthStore((s) => s.user);
  const { theme, toggleTheme } = useUIStore();

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-background/80 px-6 backdrop-blur-md">
      <div>
        <h2 className="text-sm font-semibold text-foreground">
          Welcome back, <span className="gradient-text">{user?.full_name || user?.email || 'User'}</span>
        </h2>
        <p className="text-xs text-muted-foreground">
          Role: {user?.role || 'viewer'} • Org: {user?.org_id || 'Default'}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={toggleTheme}
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-border text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
        >
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/20 text-primary">
          <User className="h-4 w-4" />
        </div>
      </div>
    </header>
  );
}
