// =========================================================
// * Volt React Dashboard
// =========================================================

// * Product Page: https://themesberg.com/product/dashboard/volt-react
// * Copyright 2021 Themesberg (https://www.themesberg.com)
// * Official Repository: https://github.com/themesberg/volt-react-dashboard
// * License: MIT License (https://themesberg.com/licensing)

// * Designed and coded by https://themesberg.com

// =========================================================

// * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. Please contact us to request a removal.

import React from 'react';
import { createRoot } from 'react-dom/client';
import { HashRouter } from "react-router-dom";

// core styles
import "./scss/volt.scss";

// vendor styles
import "react-datetime/css/react-datetime.css";

import "./i18n"; // Import i18n for English and Swahili translations

import { AuthProvider } from "./context/AuthContext";
import HomePage from "./pages/HomePage";
import ScrollToTop from "./components/ScrollToTop";

const root = createRoot(document.getElementById("root"));
root.render(
  <AuthProvider>
    <HashRouter>
      <ScrollToTop />
      <HomePage />
    </HashRouter>
  </AuthProvider>
);
