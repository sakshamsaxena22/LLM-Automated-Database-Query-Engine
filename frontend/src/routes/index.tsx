import { createBrowserRouter } from 'react-router-dom';
import { PublicLayout } from '@/components/layout/PublicLayout';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { ProtectedRoute } from '@/components/common/ProtectedRoute';

import { LandingPage } from '@/pages/public/LandingPage';
import { LoginPage } from '@/pages/public/LoginPage';
import { RegisterPage } from '@/pages/public/RegisterPage';

import { QueryConsolePage } from '@/pages/dashboard/QueryConsolePage';
import { DataManagerPage } from '@/pages/dashboard/DataManagerPage';
import { AnalyticsPage } from '@/pages/dashboard/AnalyticsPage';
import { UserManagementPage } from '@/pages/dashboard/UserManagementPage';
import { AuditLogsPage } from '@/pages/dashboard/AuditLogsPage';
import { SettingsPage } from '@/pages/dashboard/SettingsPage';
import { DatabaseConnectionsPage } from '@/pages/dashboard/DatabaseConnectionsPage';

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      { path: '/', element: <LandingPage /> },
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
    ],
  },
  {
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      { path: '/dashboard/query', element: <QueryConsolePage /> },
      { path: '/dashboard/data', element: <DataManagerPage /> },
      { path: '/dashboard/analytics', element: <AnalyticsPage /> },
      { path: '/dashboard/users', element: <UserManagementPage /> },
      { path: '/dashboard/audit', element: <AuditLogsPage /> },
      { path: '/dashboard/connections', element: <DatabaseConnectionsPage /> },
      { path: '/dashboard/settings', element: <SettingsPage /> },
    ],
  },
]);
