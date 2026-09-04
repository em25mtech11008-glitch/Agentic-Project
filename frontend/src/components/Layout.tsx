import { useState } from 'react';
import { Outlet, NavLink } from 'react-router';
import { useAuth } from '../hooks/useAuth';
import { 
  Building2, 
  LayoutDashboard, 
  Users, 
  Briefcase, 
  Headset, 
  Settings, 
  LogOut,
  BrainCircuit,
  Menu,
  X,
  Bell,
  CheckSquare
} from 'lucide-react';

export default function Layout() {
  const { user, logout, hasPermission } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  if (!user) return null;

  // Role-based navigation filtering
  const navigation = [
    { name: 'Dashboard', href: '/app/dashboard', icon: LayoutDashboard, requiredPerm: 'dashboard.view' },
    { name: 'AI Command Center', href: '/app/command-center', icon: BrainCircuit, requiredPerm: 'ai.view' },
    { name: 'Work Inbox', href: '/app/work', icon: CheckSquare, requiredPerm: 'dashboard.view' },
    { name: 'Approvals', href: '/app/approvals', icon: CheckSquare, requiredPerm: 'approvals.view' },
    { name: 'Sales & CRM', href: '/app/sales', icon: Briefcase, requiredPerm: 'sales.view' },
    { name: 'Finance', href: '/app/finance', icon: Building2, requiredPerm: 'finance.view' },
    { name: 'Support', href: '/app/support', icon: Headset, requiredPerm: 'support.view' },
    { name: 'Operations', href: '/app/operations', icon: Settings, requiredPerm: 'operations.view' },
    { name: 'HR', href: '/app/hr', icon: Users, requiredPerm: 'hr.view' },
  ].filter(item => hasPermission(item.requiredPerm));

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Mobile sidebar backdrop */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-900/80 backdrop-blur-sm lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 text-white transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex h-16 shrink-0 items-center px-6 gap-3 border-b border-gray-800 bg-gray-950/50">
          <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Building2 className="h-5 w-5" />
          </div>
          <span className="font-semibold text-lg tracking-tight">AI Command</span>
          <button className="lg:hidden ml-auto" onClick={() => setIsSidebarOpen(false)}>
            <X className="h-5 w-5 text-gray-400 hover:text-white" />
          </button>
        </div>
        
        <nav className="flex flex-1 flex-col overflow-y-auto px-4 py-6">
          <div className="space-y-1">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) => `
                  group flex gap-x-3 rounded-md p-2.5 text-sm font-medium leading-6 transition-colors
                  ${isActive 
                    ? 'bg-blue-600/10 text-blue-400' 
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                  }
                `}
                onClick={() => setIsSidebarOpen(false)}
              >
                <item.icon className="h-5 w-5 shrink-0" />
                {item.name}
              </NavLink>
            ))}
          </div>

          <div className="mt-auto pt-6">
            <button
              onClick={logout}
              className="group flex w-full gap-x-3 rounded-md p-2.5 text-sm font-medium leading-6 text-gray-400 hover:bg-red-500/10 hover:text-red-400 transition-colors"
            >
              <LogOut className="h-5 w-5 shrink-0" />
              Sign out
            </button>
          </div>
        </nav>
      </div>

      {/* Main content wrapper */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top header */}
        <header className="flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
            onClick={() => setIsSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>
          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1"></div>
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              <button type="button" className="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500">
                <Bell className="h-6 w-6" />
              </button>
              <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200" />
              <div className="flex items-center gap-x-4">
                <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center font-bold text-gray-600 text-sm">
                  {user.name.charAt(0)}
                </div>
                <div className="hidden lg:block">
                  <span className="block text-sm font-semibold leading-6 text-gray-900">{user.name}</span>
                  <span className="block text-xs text-gray-500">{user.role.replace('_', ' ')}</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main page content area (where routes inject their components) */}
        <main className="flex-1 overflow-y-auto bg-gray-50 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
