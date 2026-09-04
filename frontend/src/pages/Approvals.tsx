import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ShieldAlert, Check, X } from 'lucide-react';

interface Approval {
  id: string;
  action_type: string;
  description: string;
  status: string;
  created_at: string;
  requested_by: string;
}

export default function Approvals() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchApprovals = async () => {
      try {
        const response = await api.get('/approvals/pending');
        setApprovals(response.data.approvals || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load approvals');
      } finally {
        setLoading(false);
      }
    };
    fetchApprovals();
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
          <h3 className="font-semibold text-red-800">Error loading approvals</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Pending Approvals</h1>
        <p className="mt-1 text-sm text-gray-500">
          High-stakes AI actions requiring human authorization.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {approvals.map((approval) => (
          <div key={approval.id} className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200 flex items-center justify-between">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-orange-100 p-3 mt-1">
                <ShieldAlert className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{approval.action_type}</h3>
                <p className="mt-1 text-gray-600">{approval.description}</p>
                <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                  <span>Requested by: {approval.requested_by}</span>
                  <span>•</span>
                  <span>{new Date(approval.created_at).toLocaleString()}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button className="flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
                <X className="h-4 w-4 text-red-500" />
                Reject
              </button>
              <button className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
                <Check className="h-4 w-4" />
                Approve
              </button>
            </div>
          </div>
        ))}
        {approvals.length === 0 && (
          <div className="text-center p-12 bg-white rounded-xl ring-1 ring-gray-200">
            <ShieldAlert className="mx-auto h-12 w-12 text-gray-300" />
            <h3 className="mt-2 text-sm font-semibold text-gray-900">No pending approvals</h3>
            <p className="mt-1 text-sm text-gray-500">All actions have been reviewed.</p>
          </div>
        )}
      </div>
    </div>
  );
}
