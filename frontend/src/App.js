import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LanguageProvider } from './contexts/LanguageContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import News from './pages/News';
import ArticleDetail from './pages/ArticleDetail';
import BankCompare from './pages/BankCompare';
import Register from './pages/Register';
import Login from './pages/Login';
import Claudia from './pages/Claudia';

const HomeOrRedirect = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Claudia /> : <Home />;
};

const ProtectedClaudia = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Claudia /> : <Home />;
};

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <Router>
          <div className="App">
            <Navbar />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<HomeOrRedirect />} />
                <Route path="/news" element={<News />} />
                <Route path="/news/:id" element={<ArticleDetail />} />
                <Route path="/bank-compare" element={<BankCompare />} />
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
                <Route path="/claudia" element={<ProtectedClaudia />} />
              </Routes>
            </main>
          </div>
        </Router>
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;
