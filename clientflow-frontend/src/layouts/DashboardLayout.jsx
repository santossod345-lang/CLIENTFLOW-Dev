import DashboardSidebar from '../components/DashboardSidebar'

export default function DashboardLayout({ children }) {
  return (
    <div className="cf-shell">
      <DashboardSidebar />
      <div className="cf-main">
        {children}
      </div>
    </div>
  )
}
