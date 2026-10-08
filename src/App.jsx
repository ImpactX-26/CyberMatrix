import { useEffect } from 'react';
import { Routes, Route, Outlet, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import DemoBanner from './components/DemoBanner';
import ErrorState from './components/ErrorState';
import Landing from './pages/Landing';
import PropertySetup from './pages/PropertySetup';
import PropertyTwin from './pages/PropertyTwin';
import Investigation from './pages/Investigation';
import Portfolio from './pages/Portfolio';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import { checkBackend } from './services/api';

function Layout() {
  const { pathname } = useLocation();
  useEffect(() => { checkBackend(); }, []);
  useEffect(() => { window.scrollTo(0, 0); }, [pathname]);
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <DemoBanner />
      <main className="flex-1"><Outlet /></main>
      <footer className="border-t border-navy/10 py-6 text-center text-xs text-navy/50">
        LANDSHIELD · AI Property Change Intelligence &amp; Early Fraud Warning · Synthetic Demo Data · Findings need human/legal verification
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Landing />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/setup" element={<PropertySetup />} />
          <Route path="/property/:id" element={<PropertyTwin />} />
          <Route path="/investigation/:id" element={<Investigation />} />
          <Route path="/portfolio" element={<Portfolio />} />
        </Route>
        <Route path="*" element={<div className="px-4 py-16"><ErrorState title="Page not found" backHome /></div>} />
      </Route>
    </Routes>
  );
}
