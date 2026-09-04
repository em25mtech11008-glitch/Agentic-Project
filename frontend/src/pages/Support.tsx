import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Headset, AlertTriangle, CheckCircle, Search } from 'lucide-react';

interface Ticket {
  id: string;
  customer_id: string;
  review_score: number;
  comments: string;
  status: string;
  created_at: string;
}

export default function Support() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        const response = await api.get('/support/tickets');
        setTickets(response.data.tickets || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load support tickets');
      } finally {
        setLoading(false);
      }
    };
    fetchTickets();
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
          <h3 className="font-semibold text-red-800">Error loading tickets</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const filteredTickets = tickets.filter(ticket => 
    ticket.comments?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    ticket.customer_id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 p-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Support Tickets</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage customer inquiries, low-score reviews, and support requests.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search tickets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
          <div className="absolute -right-4 -top-4 rounded-full bg-orange-50 p-8">
            <AlertTriangle className="h-8 w-8 text-orange-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">Open Tickets</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
              {tickets.length}
            </dd>
          </div>
        </div>
      </div>

      <div className="rounded-xl bg-white shadow-sm ring-1 ring-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Review Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Issue</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTickets.map((ticket) => (
                <tr key={ticket.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {ticket.customer_id || 'Unknown'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      ticket.review_score <= 2 ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {ticket.review_score} / 5
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    <div className="max-w-md truncate">{ticket.comments || 'No comment provided'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900 flex items-center justify-end gap-1 w-full">
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
              {filteredTickets.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-sm text-gray-500">
                    No tickets found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
