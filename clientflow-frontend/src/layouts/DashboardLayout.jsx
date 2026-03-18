import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'

export default function DashboardLayout({ children }) {
  console.log('[DashboardLayout] render shell')

  return (
    <div className="cf-shell">
      <Sidebar />
      <main className="cf-main">{children || <Outlet />}</main>
    </div>
  )
}
