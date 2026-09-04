import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { FileText, DollarSign, TrendingUp, AlertCircle } from 'lucide-react';

interface Invoice {
  id: string;
  customer_id: string;
  amount: number;
  status: string;
  due_date: string;
}

interface Expense {
  id: string;
  category: string;
  amount: number;
  date: string;
  vendor: string;
}

export default function Finance() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFinanceData = async () => {
      try {
        const [invoicesRes, expensesRes] = await Promise.all([
          api.get('/finance/invoices'),
          api.get('/finance/expenses')
        ]);
        setInvoices(invoicesRes.data.invoices || []);
        setExpenses(expensesRes.data.expenses || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load finance data');
      } finally {
        setLoading(false);
      }
    };
    fetchFinanceData();
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
          <h3 className="font-semibold text-red-800">Error loading finance data</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const totalInvoices = invoices.reduce((sum, inv) => sum + inv.amount, 0);
  const overdueInvoices = invoices.filter(inv => inv.status.toLowerCase() === 'overdue').reduce((sum, inv) => sum + inv.amount, 0);
  const totalExpenses = expenses.reduce((sum, exp) => sum + exp.amount, 0);

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Finance</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage invoices, expenses, and track financial health.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
          <div className="absolute -right-4 -top-4 rounded-full bg-blue-50 p-8">
            <DollarSign className="h-8 w-8 text-blue-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">Total Receivables</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
              ${totalInvoices.toLocaleString()}
            </dd>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
          <div className="absolute -right-4 -top-4 rounded-full bg-red-50 p-8">
            <AlertCircle className="h-8 w-8 text-red-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">Overdue Invoices</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-red-600">
              ${overdueInvoices.toLocaleString()}
            </dd>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
          <div className="absolute -right-4 -top-4 rounded-full bg-purple-50 p-8">
            <TrendingUp className="h-8 w-8 text-purple-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">Total Expenses</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
              ${totalExpenses.toLocaleString()}
            </dd>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Invoices Table */}
        <div className="rounded-xl bg-white shadow-sm ring-1 ring-gray-200">
          <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <FileText className="h-5 w-5 text-gray-500" />
              Recent Invoices
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {invoices.slice(0, 5).map((invoice) => (
                  <tr key={invoice.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        invoice.status.toLowerCase() === 'paid' ? 'bg-green-100 text-green-800' :
                        invoice.status.toLowerCase() === 'overdue' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      ${invoice.amount.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(invoice.due_date).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
                {invoices.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-6 py-4 text-center text-sm text-gray-500">No invoices found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Expenses Table */}
        <div className="rounded-xl bg-white shadow-sm ring-1 ring-gray-200">
          <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-gray-500" />
              Recent Expenses
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {expenses.slice(0, 5).map((expense) => (
                  <tr key={expense.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {expense.category}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {expense.vendor}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      ${expense.amount.toLocaleString()}
                    </td>
                  </tr>
                ))}
                {expenses.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-6 py-4 text-center text-sm text-gray-500">No expenses found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
