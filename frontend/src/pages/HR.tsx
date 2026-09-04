import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Users, Briefcase, Mail } from 'lucide-react';

interface Employee {
  id: string;
  name: string;
  email: string;
  department: string;
  role: string;
}

export default function HR() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const response = await api.get('/hr/employees');
        setEmployees(response.data.employees || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load employees data');
      } finally {
        setLoading(false);
      }
    };
    fetchEmployees();
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
          <h3 className="font-semibold text-red-800">Error loading HR data</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const departments = [...new Set(employees.map(e => e.department))];

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Human Resources</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage employee directory and department structures.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
          <div className="absolute -right-4 -top-4 rounded-full bg-blue-50 p-8">
            <Users className="h-8 w-8 text-blue-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">Total Employees</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
              {employees.length}
            </dd>
          </div>
        </div>
        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
          <div className="absolute -right-4 -top-4 rounded-full bg-purple-50 p-8">
            <Briefcase className="h-8 w-8 text-purple-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">Departments</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
              {departments.length}
            </dd>
          </div>
        </div>
      </div>

      <div className="rounded-xl bg-white shadow-sm ring-1 ring-gray-200 overflow-hidden">
        <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <Users className="h-5 w-5 text-gray-500" />
            Employee Directory
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {employees.map((employee) => (
                <tr key={employee.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center font-bold text-gray-600">
                        {employee.name.charAt(0)}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{employee.name}</div>
                        <div className="text-sm text-gray-500 flex items-center gap-1">
                          <Mail className="h-3 w-3" /> {employee.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                      {employee.department || 'General'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {employee.role || 'Staff'}
                  </td>
                </tr>
              ))}
              {employees.length === 0 && (
                <tr>
                  <td colSpan={3} className="px-6 py-8 text-center text-sm text-gray-500">
                    No employees found.
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
