import { useAuthStore } from '@/store/authStore';
import { Settings, User, Mail, Shield } from 'lucide-react';

export function SettingsPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <Settings className="h-6 w-6 text-primary" />
          Settings
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">Account and platform settings</p>
      </div>

      <div className="glass rounded-2xl p-6 space-y-6 max-w-2xl">
        <h2 className="text-lg font-semibold text-foreground">Profile</h2>

        <div className="grid gap-4">
          <div className="flex items-center gap-4 rounded-xl border border-border bg-background p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <User className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Full Name</div>
              <div className="text-sm font-medium text-foreground">{user?.full_name || '—'}</div>
            </div>
          </div>

          <div className="flex items-center gap-4 rounded-xl border border-border bg-background p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-chart-2/10 text-chart-2">
              <Mail className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Email</div>
              <div className="text-sm font-medium text-foreground">{user?.email || '—'}</div>
            </div>
          </div>

          <div className="flex items-center gap-4 rounded-xl border border-border bg-background p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-chart-4/10 text-chart-4">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Role</div>
              <div className="text-sm font-medium text-foreground capitalize">{user?.role || 'viewer'}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
