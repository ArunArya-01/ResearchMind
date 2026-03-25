
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';

import Report from './pages/Report';

import Analysis from './pages/Analysis';

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/report" element={<Report />} />
          <Route path="/analysis" element={<Analysis />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
