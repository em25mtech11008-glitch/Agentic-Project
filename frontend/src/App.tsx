import { BrowserRouter, Routes, Route, Navigate } from 'react-router';
import { useAuth } from './hooks/useAuth';
import Login from './pages/Login';
import Layout from './components/Layout';

import Dashboard from './pages/Dashboard';
import Finance from './pages/Finance';
import Sales from './pages/Sales';
import CommandCenter from './pages/CommandCenter';
import Support from './pages/Support';
import Operations from './pages/Operations';
import HR from './pages/HR';
import Approvals from './pages/Approvals';
import WorkInbox from './pages/WorkInbox';

// A simple wrapper to protect routes
const ProtectedRoute = ({ children, requiredPerm }: { children: React.ReactNode, requiredPerm?: string }) => {
  const { isAuthenticated, isLoading, hasPermission } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredPerm && !hasPermission(requiredPerm)) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900">Access Denied</h2>
        <p className="mt-2 text-gray-600">You do not have permission to view this page.</p>
      </div>
    );
  }

  return children;
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
        
        <Route path="/app" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route path="dashboard" element={
            <ProtectedRoute requiredPerm="dashboard.view">
              <Dashboard />
            </ProtectedRoute>
          } />
          
          <Route path="command-center" element={
            <ProtectedRoute requiredPerm="ai.view">
              <CommandCenter />
            </ProtectedRoute>
          } />
          
          {/* Main App Modules */}
          <Route path="work" element={<WorkInbox />} />
          <Route path="approvals" element={<Approvals />} />
          <Route path="sales" element={<Sales />} />
          <Route path="finance" element={<Finance />} />
          <Route path="support" element={<Support />} />
          <Route path="operations" element={<Operations />} />
          <Route path="hr" element={<HR />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
