import os

docs_dir = "d:/myprojects/AMAS FARM/AMAS-FARM-Management-System/docs"
os.makedirs(docs_dir, exist_ok=True)
output_path = os.path.join(docs_dir, 'frontend.md')

md = []

md.append("# AMAS FARM Frontend Documentation\n")

md.append("## 1. Frontend Overview")
md.append("The AMAS FARM frontend is a Single Page Application (SPA) built with **React 18** and **Vite**. The UI is constructed using the **Volt React Dashboard** template (Bootstrap 5) by Themesberg. The application provides a comprehensive administrative interface for managing farm operations, point-of-sale, human resources, inventory, and finance.\n")

md.append("## 2. Architecture & Tech Stack")
md.append("""* **Core Framework**: React 18
* **Build Tool**: Vite (Replaced Create React App)
* **Routing**: React Router DOM v5 (Note: Uses `Switch` and `Route` from v5 paradigm)
* **Styling**: Bootstrap 5 + SCSS (Themesberg Volt UI Kit)
* **State Management**: React Context API (`AuthContext`) + Local Component State (`useState`, `useEffect`)
* **API Client**: Axios (Configured with interceptors)
* **Charts & Data Viz**: Recharts (for complex graphs) & Chartist
* **Date & Time Handling**: Moment.js
* **Alerts & Notifications**: SweetAlert2
* **Internationalization (i18n)**: i18next / react-i18next
""")

md.append("## 3. Directory Structure")
md.append("""```text
frontend/
|-- package.json        # Dependencies and build scripts
|-- vite.config.js      # Vite build configuration
|-- public/             # Static assets (Favicons, manifest)
`-- src/
    |-- api/            # API configuration (axios.js)
    |-- assets/         # SCSS stylesheets, images, icons
    |-- components/     # Reusable UI (Sidebar, Navbar, Footer, Preloader)
    |-- context/        # React Context providers (AuthContext.jsx)
    |-- pages/          # Feature-based route components grouped by module
    |   |-- admin/
    |   |-- assets/
    |   |-- dashboard/
    |   |-- examples/   # Auth pages (Sign In, 404, 500)
    |   |-- farm/
    |   |-- finance/
    |   |-- hr/
    |   |-- inventory/
    |   |-- pos/
    |   `-- reports/
    |-- routes.js       # Centralized route paths object mapping
    `-- HomePage.jsx    # Main router wrapper and Private Route enforcement
```
""")

md.append("## 4. API Integration & Axios Configuration")
md.append("All network requests route through a globally configured Axios instance located at `src/api/axios.js`.")
md.append("""### Axios Interceptors
The application implements two critical interceptors:
1. **Request Interceptor**: Automatically retrieves the `access_token` from `localStorage` and appends `Authorization: Bearer <token>` to the headers of every outgoing request.
2. **Response Interceptor**: Listens for `401 Unauthorized` responses globally. If triggered, it removes the invalid token and dispatches a custom `auth:unauthorized` window event to force a logout across the application.
""")

md.append("## 5. State Management")
md.append("""The frontend avoids heavy global state managers like Redux in favor of a lightweight approach:

1. **Global Auth State (`AuthContext.jsx`)**:
   Manages the current logged-in `user` state, `loading` flags, and handles the `login()` and `logout()` lifecycle. It automatically fetches `/api/v1/user/me` on initialization if a token is present in localStorage.
2. **Local Component State**:
   Page components fetch their own data using `useEffect` and store it using `useState`. Tables and forms manage their own pagination, filtering, and submission logic.
""")

md.append("## 6. Authentication & Protected Routes")
md.append("""### The `RouteWithSidebar` Higher-Order Component (HOC)
Routing is managed primarily inside `src/pages/HomePage.jsx`. The application uses a custom `RouteWithSidebar` wrapper component that acts as a **Private Route**.

```jsx
// Concept of RouteWithSidebar
const RouteWithSidebar = ({ component: Component, ...rest }) => {
  const { user } = useAuth();
  
  return (
    <Route {...rest} render={props => {
      // 1. Protect the route - Redirect if not authenticated
      if (!user) return <Redirect to={Routes.Signin.path} />;

      // 2. Render the application shell (Sidebar, Navbar, Footer) + Content
      return (
        <>
          <Sidebar />
          <main className="content d-flex flex-column min-vh-100">
            <Navbar />
            <Component {...props} />
            <Footer />
          </main>
        </>
      );
    }} />
  );
};
```
""")

md.append("## 7. Subsystem Routing Map")
md.append("Paths are centrally defined in `src/routes.js`. Major modules include:")
md.append("""### Core & Auth
* `/` - Dashboard Overview
* `/examples/sign-in` - Login Page
* `/settings` - User Profile & Settings

### Farm Operations
* `/farm/houses` - Manage Houses
* `/farm/flocks` - Manage Flocks
* `/farm/productions` - Egg Production Logs
* `/farm/feeds`, `/farm/medications`, `/farm/vaccinations`, `/farm/mortalities`
* `/farm/report` - Farm Master Summary

### Inventory
* `/inventory/categories` - Product Categories
* `/inventory/products` - Product Catalog
* `/inventory/stock-movements` - Stock In/Out Logs
* `/inventory/status` - Live Stock Overview

### Business (Point of Sale)
* `/pos/customers` - Customer CRM
* `/pos/suppliers` - Supplier CRM
* `/pos/sales` - Sales Invoices
* `/pos/purchases` - Purchase Orders
* `/pos/expenses` - Operational Expenses

### Human Resources & Assets
* `/hr/employees` - Employee Directory
* `/hr/payroll` - Salary and Payroll Management
* `/assets/list` - Farm Assets

### Finance
* `/finance/dashboard` - Top-level Financial KPIs
* `/finance/accounts` - Chart of Accounts
* `/finance/transactions` - General Ledger
* `/finance/debts` - Receivables & Payables
* `/finance/reports` - Trial Balance, P&L, Cash Flow, Balance Sheet
""")

md.append("## 8. Build & Development")
md.append("""The frontend is orchestrated by Vite, providing rapid Hot Module Replacement (HMR).

### Commands
* **Start Development Server**: `npm run dev` or `npm start`
* **Build for Production**: `npm run build`
* **Preview Production Build**: `npm run preview`

### Environment Variables
Vite requires environment variables to be prefixed with `VITE_`.
The API base URL is resolved dynamically via `import.meta.env.VITE_API_BASE_URL` with a fallback to `http://127.0.0.1:8000`.
""")

md.append("## 9. Common UI Conventions")
md.append("""* **Tables**: Wrapped in Bootstrap `Card` and `Table` components from `@themesberg/react-bootstrap`.
* **Icons**: Powered by `@fortawesome/react-fontawesome`.
* **Notifications**: Use `Swal.fire()` (SweetAlert2) for success/error popups instead of standard browser alerts.
* **Date Formatting**: `moment(dateString).format("YYYY-MM-DD")` is standard across forms and tables.
""")

md.append("## 10. Frontend Maintenance Notes")
md.append("""When adding a new frontend feature:
1. Define the new route path in `src/routes.js`.
2. Create the UI Component inside the appropriate module folder in `src/pages/`.
3. Map the route to the component in `src/pages/HomePage.jsx` using `<RouteWithSidebar>`.
4. Ensure all API calls are made using the exported `api` object from `src/api/axios.js` to inherit the authentication interceptors.
""")

with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))

print("Frontend Markdown generated successfully.")
