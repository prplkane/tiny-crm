import { Routes, Route, Link } from 'react-router-dom'
import Clients from './pages/Clients';
import Deals from './pages/Deals';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow p-4 flex gap-4">
        <Link to="/clients" className="text-blue-600 hover:underline">Clients</Link>
        <Link to="/deals" className="text-blue-600 hover:underline">Deals</Link>
      </nav>

      <main className="p-4">
        <Routes>
          <Route path="/clients" element={<Clients />} />
          <Route path="/deals" element={<Deals />} />
          <Route path="/" element={<div>Welcome to Tiny CRM</div>} />
        </Routes>
      </main>
    </div>
  )
}

export default App
