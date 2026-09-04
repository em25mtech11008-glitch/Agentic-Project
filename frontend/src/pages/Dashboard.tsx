import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Users, ShoppingCart, CheckSquare, Clock } from 'lucide-react';

interface DashboardMetrics {
  customers: number;
  orders: number;
  tasks: number;
  pending_approvals: number;
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await api.get('/dashboard/');
        setMetrics(response.data.metrics);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-50/50">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="rounded-lg bg-red-50 p-4 text-red-600">
          <h3 className="font-semibold text-red-800">Error loading dashboard</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your company's operational health.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* Customers Card */}
        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200 transition-all hover:shadow-md hover:ring-gray-300">
          <div className="absolute -right-4 -top-4 rounded-full bg-blue-50 p-8">
            <Users className="h-8 w-8 text-blue-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">Total Customers</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
              {metrics?.customers || 0}
            </dd>
          </div>
        </div>

        {/* Orders Card */}
        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200 transition-all hover:shadow-md hover:ring-gray-300">
          <div className="absolute -right-4 -top-4 rounded-full bg-emerald-50 p-8">
            <ShoppingCart className="h-8 w-8 text-emerald-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">Active Orders</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
              {metrics?.orders || 0}
            </dd>
          </div>
        </div>

        {/* Tasks Card */}
        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200 transition-all hover:shadow-md hover:ring-gray-300">
          <div className="absolute -right-4 -top-4 rounded-full bg-indigo-50 p-8">
            <CheckSquare className="h-8 w-8 text-indigo-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">Open Tasks</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
              {metrics?.tasks || 0}
            </dd>
          </div>
        </div>

        {/* Pending Approvals Card */}
        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200 transition-all hover:shadow-md hover:ring-gray-300">
          <div className="absolute -right-4 -top-4 rounded-full bg-amber-50 p-8">
            <Clock className="h-8 w-8 text-amber-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">Pending Approvals</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-amber-600">
              {metrics?.pending_approvals || 0}
            </dd>
          </div>
        </div>
      </div>
    </div>
  );
}
