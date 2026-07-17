import React from 'react';  // Import React here
import LoginPage from './pages/LoginPage';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import NavPage from './pages/NavPage';  // Import the NavPage component here
import UserManagePage from './pages/UserManagePage';  // Import the UserManagePage component here
import RegisterPage from './pages/RegisterPage';  // Import the RegisterPage component here
import RequireAuth from './components/RequireAuth';  // Import the RequiredAuth component here
function App() {
    return(
        <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<LoginPage/>}></Route>
            <Route path="/register" element={<RegisterPage/>}></Route>

            <Route element={<RequireAuth />}>
                <Route path='/navpage' element={<NavPage />}></Route>
                <Route path='/usermanage' element={<UserManagePage />}></Route>  // Add this line to include the login route
            </Route>
       </Routes>
    )
}

export default App;
