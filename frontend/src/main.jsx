import { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import AlaafiaPage from './AlaafiaPage';
import AlaafiaAdminPage from './AlaafiaAdminPage';
import './index.css';

// Hand-rolled path switch (same approach as the Ìyàwó frontend — no router dep).
//   /            → public page
//   /alaafia     → public page (kept so old iyawo.org links still resolve)
//   /admin       → access-request review
//   /alaafia-admin → access-request review (old path)
const ADMIN_PATHS = new Set(['/admin', '/alaafia-admin']);

function App() {
  const [path, setPath] = useState(window.location.pathname);

  useEffect(() => {
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  return ADMIN_PATHS.has(path) ? <AlaafiaAdminPage /> : <AlaafiaPage />;
}

createRoot(document.getElementById('root')).render(<App />);
