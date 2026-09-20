import os

files = [
    ('CashBookReport.jsx', 'Cash', 'Cash Book'),
    ('BankBookReport.jsx', 'Bank', 'Bank Book'),
    ('MobileMoneyReport.jsx', 'Mobile Money', 'Mobile Money Book')
]

base_path = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/pages/reports/financial/'

for filename, acc_type, title in files:
    filepath = os.path.join(base_path, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = f'''import React, {{ useState, useEffect }} from "react";
import {{ Badge }} from "@themesberg/react-bootstrap";
import {{ faArrowRight, faArrowLeft, faWallet, faPiggyBank, faUniversity, faMobileAlt }} from "@fortawesome/free-solid-svg-icons";
import {{ ReportPageHeader }} from "../components/ReportPageHeader";
import {{ ReportFilters }} from "../components/ReportFilters";
import {{ ReportSummaryCards }} from "../components/ReportSummaryCards";
import {{ ReportTable }} from "../components/ReportTable";
import {{ reportsApi }} from "../../../api/reportsApi";
import {{ api }} from "../../../api/axios";
import moment from "moment";

export default () => {{
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const [accounts, setAccounts] = useState([]);
  
  const [filterValues, setFilterValues] = useState({{
    date_from: "",
    date_to: "",
    account_id: "",
    transaction_type: "",
    direction: ""
  }});

  const fetchAccounts = async () => {{
    try {{
      const res = await api.get("/api/v1/finance/accounts/?limit=100");
      const items = res.data.items || res.data;
      const filtered = items.filter(a => a.account_type === "{acc_type}");
      const options = filtered.map(acc => ({{ value: acc.id, label: acc.account_name }}));
      setAccounts(options);
      
      // Auto-select first account if available
      if (options.length > 0) {{
          setFilterValues(prev => ({{ ...prev, account_id: options[0].value }}));
          fetchReport(1, options[0].value);
      }} else {{
          setError("No {acc_type} accounts found. Please create one first.");
      }}
    }} catch (err) {{
      console.error("Failed to fetch accounts", err);
    }}
  }};

  const fetchReport = async (currentPage = page, customAccountId = null) => {{
    const accId = customAccountId || filterValues.account_id;
    if (!accId) return; // Do not fetch if no account selected
    
    setLoading(true);
    setError(null);
    try {{
      const params = {{ ...filterValues, account_id: accId, page: currentPage, limit: 10 }};
      let res;
      if ("{acc_type}" === "Cash") res = await reportsApi.getCashBook(params);
      else if ("{acc_type}" === "Bank") res = await reportsApi.getBankBook(params);
      else res = await reportsApi.getMobileBook(params);
      
      setData(res.data.items || []);
      setTotalPages(res.data.pages || 1);
      setPage(res.data.page || 1);
      
      setSummary({{
        opening_balance: res.data.opening_balance,
        total_money_in: res.data.total_money_in,
        total_money_out: res.data.total_money_out,
        closing_balance: res.data.closing_balance
      }});
    }} catch (err) {{
      const errDetail = err.response?.data?.detail;
      setError(typeof errDetail === 'object' ? JSON.stringify(errDetail) : errDetail || "Unable to load report. Try again.");
    }} finally {{
      setLoading(false);
    }}
  }};

  useEffect(() => {{
    fetchAccounts();
  }}, []);

  const handleFilterChange = (name, value) => {{
    setFilterValues(prev => ({{ ...prev, [name]: value }}));
  }};

  const handleApplyFilters = () => fetchReport(1);

  const handleResetFilters = () => {{
    if (accounts.length > 0) {{
        setFilterValues({{ date_from: "", date_to: "", account_id: accounts[0].value, transaction_type: "", direction: "" }});
        setPage(1);
        setTimeout(() => fetchReport(1, accounts[0].value), 0);
    }}
  }};

  const filters = [
    {{ name: "date_from", label: "Date From", type: "date", value: filterValues.date_from }},
    {{ name: "date_to", label: "Date To", type: "date", value: filterValues.date_to }},
    {{ name: "account_id", label: "Account", type: "select", value: filterValues.account_id, options: accounts }},
    {{ 
      name: "transaction_type", label: "Type", type: "select", value: filterValues.transaction_type, 
      options: [
        {{ value: "SALE", label: "Sale" }},
        {{ value: "PURCHASE", label: "Purchase" }},
        {{ value: "EXPENSE", label: "Expense" }},
        {{ value: "PAYROLL", label: "Payroll" }},
        {{ value: "TRANSFER", label: "Transfer" }},
        {{ value: "MANUAL", label: "Manual" }}
      ]
    }},
    {{
      name: "direction", label: "Direction", type: "select", value: filterValues.direction,
      options: [
        {{ value: "IN", label: "Money IN" }},
        {{ value: "OUT", label: "Money OUT" }}
      ]
    }}
  ];

  const columns = [
    {{ header: "Date", render: (row) => moment(row.transaction_date).format("YYYY-MM-DD HH:mm") }},
    {{ header: "Reference", accessor: "reference_number" }},
    {{ header: "Description", accessor: "description" }},
    {{ header: "Type", render: (row) => <Badge bg="info">{{row.transaction_type}}</Badge> }},
    {{ 
      header: "Money IN", 
      render: (row) => row.direction === "IN" ? <span className="text-success fw-bold">{{parseFloat(row.amount).toLocaleString()}}</span> : "-" 
    }},
    {{ 
      header: "Money OUT", 
      render: (row) => row.direction === "OUT" ? <span className="text-danger fw-bold">{{parseFloat(row.amount).toLocaleString()}}</span> : "-" 
    }},
    {{ 
      header: "Balance", 
      render: (row) => <span className="fw-bold">{{parseFloat(row.running_balance).toLocaleString()}}</span> 
    }}
  ];

  let icon = faPiggyBank;
  if ("{acc_type}" === "Bank") icon = faUniversity;
  if ("{acc_type}" === "Mobile Money") icon = faMobileAlt;

  const summaryCards = summary ? [
    {{ title: "Opening Balance", value: parseFloat(summary.opening_balance).toLocaleString(), icon: faPiggyBank, iconColor: "secondary" }},
    {{ title: "Total Money IN", value: parseFloat(summary.total_money_in).toLocaleString(), icon: faArrowRight, iconColor: "success" }},
    {{ title: "Total Money OUT", value: parseFloat(summary.total_money_out).toLocaleString(), icon: faArrowLeft, iconColor: "danger" }},
    {{ title: "Closing Balance", value: parseFloat(summary.closing_balance).toLocaleString(), icon: icon, iconColor: "primary" }},
  ] : [];

  return (
    <>
      <ReportPageHeader 
        title="{title}" 
        subtitle="Summary and running balance of all {acc_type.lower()} transactions."
        breadcrumbs={{[{{ label: "Financial" }}, {{ label: "{title}" }}]}}
      />
      
      <ReportFilters 
        filters={{filters}} 
        onFilterChange={{handleFilterChange}} 
        onApply={{handleApplyFilters}} 
        onReset={{handleResetFilters}} 
        loading={{loading}}
      />

      {{!loading && !error && summary && <ReportSummaryCards items={{summaryCards}} />}}
      
      <ReportTable 
        columns={{columns}} 
        data={{data}} 
        loading={{loading}} 
        error={{error}} 
        page={{page}} 
        totalPages={{totalPages}} 
        onPageChange={{fetchReport}} 
      />
    </>
  );
}}'''
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("Updated book reports")
