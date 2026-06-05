import { useState, useEffect } from 'react';
import apiClient from '@/api/client';
import { Users, Shield, Loader2 } from 'lucide-react';

interface UserItem {
  _id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at?: string;
}

export function UserManagementPage() {
  const [users, setUsers] = useState<UserItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get('/users/')
      .then(({ data }) => {
        setUsers(data.users || []);
        setTotal(data.total || 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const updateRole = async (userId: string, role: string) => {
    try {
      await apiClient.put(`/users/${userId}`, { role });
      setUsers((prev) =>
        prev.map((u) => (u._id === userId ? { ...u, role } : u))
      );
    } catch {}
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <Users className="h-6 w-6 text-primary" />
          User Management
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">{total} registered users</p>
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/30">
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground">User</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground">Email</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground">Role</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground">Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user._id} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                <td className="px-4 py-3 font-medium text-foreground">{user.full_name || '—'}</td>
                <td className="px-4 py-3 text-muted-foreground">{user.email}</td>
                <td className="px-4 py-3">
                  <select
                    value={user.role}
                    onChange={(e) => updateRole(user._id, e.target.value)}
                    className="rounded border border-border bg-background px-2 py-1 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    {['viewer', 'editor', 'manager', 'admin', 'super_admin'].map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                    user.is_active !== false
                      ? 'bg-chart-2/10 text-chart-2'
                      : 'bg-destructive/10 text-destructive'
                  }`}>
                    <span className={`h-1.5 w-1.5 rounded-full ${user.is_active !== false ? 'bg-chart-2' : 'bg-destructive'}`} />
                    {user.is_active !== false ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
