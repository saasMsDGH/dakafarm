import React, { useState, useEffect, useRef } from "react";
import { Card, Button, Spinner, Alert, Form, Row, Col, Table } from "@themesberg/react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPrint, faSyncAlt } from "@fortawesome/free-solid-svg-icons";
import { 
    ResponsiveContainer, 
    BarChart, 
    Bar, 
    XAxis, 
    YAxis, 
    Tooltip, 
    Cell, 
    PieChart, 
    Pie,
    LabelList
} from "recharts";
import { reportsApi } from "../../api/reportsApi";
import moment from "moment";
import { useReactToPrint } from 'react-to-print';

export default () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [dateRange, setDateRange] = useState({ date_from: '', date_to: '' });

    const reportRef = useRef();

    const fetchSummary = async (overrideRange) => {
        setLoading(true);
        setError(null);
        try {
            const rangeToUse = overrideRange || dateRange;
            const res = await reportsApi.getMasterSummary(rangeToUse);
            setData(res.data);
        } catch (err) {
            console.error("Failed to fetch master summary:", err);
            setError("Unable to load the farm operations report. Please check server connection.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSummary();
    }, []);

    const handlePrint = useReactToPrint({
        contentRef: reportRef,
        documentTitle: `AMAS_FARM_Executive_Report_${moment().format('YYYYMMDD')}`,
    });

    const formatMoney = (val) => {
        return Number(val || 0).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    };

    const setQuickRange = (type) => {
        let from = '';
        let to = moment().format('YYYY-MM-DD');

        if (type === 'today') {
            from = moment().format('YYYY-MM-DD');
        } else if (type === 'month') {
            from = moment().startOf('month').format('YYYY-MM-DD');
        } else if (type === 'last30') {
            from = moment().subtract(30, 'days').format('YYYY-MM-DD');
        } else if (type === 'ytd') {
            from = moment().startOf('year').format('YYYY-MM-DD');
        } else if (type === 'all') {
            from = '';
            to = '';
        }

        const newRange = { date_from: from, date_to: to };
        setDateRange(newRange);
        fetchSummary(newRange);
    };

    const renderOfficialReport = () => {
        if (!data) return null;

        const generatedOn = moment(data.generated_on).format('DD MMM YYYY');
        const reportRefNo = data.report_reference || `AF-OPR${moment().format('YYYYMMDD-HHmm')}`;

        const f = data.financial_overview || {};
        const c = data.cash_position || {};
        const o = data.farm_operations || {};
        const inv = data.inventory_summary || {};
        const ast = data.asset_summary || {};
        const hr = data.hr_summary || {};
        const cs = data.customers_suppliers || {};
        const kpi = data.executive_kpis || {};

        // 1. Finance Calculations
        const totalSales = Number(f.total_sales || 0);
        const cogs = Number(f.total_cogs || f.total_purchases || 0);
        const expenses = Number(f.total_expenses || 0);
        const payroll = Number(f.total_payroll || 0);
        const farmCosts = cogs + expenses + payroll;
        const netProfit = Number(f.net_profit || 0);
        const cashAvailable = Number(c.total_available || 0);
        const totalWealth = Number(ast.total_asset_cost || 0) + Number(inv.total_valuation || 0);

        const salesKeptPct = totalSales > 0 ? ((netProfit / totalSales) * 100).toFixed(1) : "0.0";
        const cogsPer100 = totalSales > 0 ? Math.round((cogs / totalSales) * 100) : 0;
        const costsPer100 = totalSales > 0 ? Math.round((expenses / totalSales) * 100) : 0;
        const wagesPer100 = totalSales > 0 ? Math.round((payroll / totalSales) * 100) : 0;
        const profitPer100 = totalSales > 0 ? Math.round((netProfit / totalSales) * 100) : 0;

        // Horizontal Bar Chart Data (Page 1)
        const whereMoneyWentData = [
            { name: "Money In (Sales)", amount: totalSales, fill: "#2563EB", label: `TZS ${(totalSales / 1000000).toFixed(2)}M` },
            { name: "Feed & Stock", amount: cogs, fill: "#A16207", label: `TZS ${(cogs / 1000000).toFixed(1)}M` },
            { name: "Running Costs", amount: expenses, fill: "#D97706", label: `TZS ${formatMoney(expenses)}` },
            { name: "Wages", amount: payroll, fill: "#F59E0B", label: `TZS ${formatMoney(payroll)}` },
            { name: "Profit Left", amount: Math.max(0, netProfit), fill: "#10B981", label: `TZS ${formatMoney(netProfit)}` },
        ];

        // 2. Cash & Debt Calculations (Page 2)
        const cashSafe = Number(c.cash || 0);
        const bank = Number(c.bank || 0);
        const mobileMoney = Number(c.mobile_money || 0);

        const rawCashData = [
            { name: "Farm Safe", value: cashSafe, fill: "#F59E0B" },
            { name: "Bank", value: bank, fill: "#2563EB" },
            { name: "Mobile Money", value: mobileMoney, fill: "#0D9488" },
        ].filter(d => d.value > 0);
        const cashChartData = rawCashData.length > 0 ? rawCashData : [{ name: "No Funds", value: 1, fill: "#E2E8F0" }];

        const customerOwed = Number(c.customer_outstanding || cs.customer_outstanding || 0);
        const supplierPayable = Number(c.supplier_payable || cs.supplier_payable || 0);
        const netCashPosition = Number(c.net_working_capital || (cashAvailable + customerOwed - supplierPayable));

        let topCashAccount = "bank";
        if (cashSafe >= bank && cashSafe >= mobileMoney) topCashAccount = "farm safe";
        else if (mobileMoney >= bank && mobileMoney >= cashSafe) topCashAccount = "mobile money wallets";
        else topCashAccount = "bank";

        let liquidityNarrative = "";
        if (cashAvailable >= supplierPayable * 1.5 && cashAvailable > 0) {
            liquidityNarrative = `Most of the farm's ready cash sits in the ${topCashAccount}. Against TZS ${formatMoney(supplierPayable)} owed to suppliers and TZS ${formatMoney(customerOwed)} owed by customers, the farm's own system marks this as a strong liquidity position — enough ready cash to cover what it owes several times over.`;
        } else if (cashAvailable >= supplierPayable) {
            liquidityNarrative = `Most of the farm's ready cash sits in the ${topCashAccount}. The farm holds enough cash on hand to clear all current supplier bills of TZS ${formatMoney(supplierPayable)}, leaving TZS ${formatMoney(netCashPosition)} in surplus working capital.`;
        } else {
            liquidityNarrative = `The farm has TZS ${formatMoney(supplierPayable)} in supplier bills coming due with TZS ${formatMoney(cashAvailable)} in ready cash. Collecting the TZS ${formatMoney(customerOwed)} owed by customers will be important to settle supplier commitments smoothly.`;
        }

        // 3. Poultry Operations Calculations (Page 3)
        const eggsHarvested = Number(o.eggs_produced || 0);
        const goodEggs = Number(o.good_eggs || 0);
        const damagedEggs = Number(o.damaged_eggs || 0);
        const birdsLost = Number(o.total_mortality || 0);
        const currentBirds = Number(o.total_birds || 0);
        const layingRateNum = parseFloat(o.average_laying_rate || 0);

        const goodEggPct = eggsHarvested > 0 ? ((goodEggs / eggsHarvested) * 100).toFixed(1) : "100.0";
        const damagedEggPct = eggsHarvested > 0 ? ((damagedEggs / eggsHarvested) * 100).toFixed(1) : "0.0";

        const eggChartData = (eggsHarvested > 0) ? [
            { name: "Good for sale", value: goodEggs, fill: "#10B981" },
            { name: "Cracked/damaged", value: damagedEggs, fill: "#EF4444" },
        ] : [
            { name: "No Eggs Collected", value: 1, fill: "#E2E8F0" }
        ];

        // Data integrity check:
        const hasContradiction = currentBirds === 0 && (eggsHarvested > 0 || birdsLost > 0);

        // 4. Assets & Team Calculations (Page 4)
        const assetCost = Number(ast.total_asset_cost || 0);
        const stockValuation = Number(inv.total_valuation || 0);
        const assetPayable = Number(ast.total_payable || 0);
        const lowStockCount = Number(inv.low_stock_count || 0) + Number(inv.out_of_stock_count || 0);

        const propertyBarData = [
            { name: "Equipment & Machinery", amount: assetCost, fill: "#1B4332", displayVal: `TZS ${formatMoney(assetCost)}` },
            { name: "Feed & Supplies in Store", amount: stockValuation, fill: "#D97706", displayVal: `TZS ${formatMoney(stockValuation)}` },
        ];

        let propertyFractionText = "three-quarters";
        if (totalWealth > 0) {
            const ratio = assetCost / totalWealth;
            if (ratio >= 0.7) propertyFractionText = "three-quarters";
            else if (ratio >= 0.55) propertyFractionText = "about two-thirds";
            else if (ratio >= 0.45) propertyFractionText = "about half";
            else propertyFractionText = "one-third";
        }

        const netSalaries = Number(hr.net_payroll_liability || 0);
        const paidSalaries = Number(hr.paid_payroll || 0);
        const pendingSalaries = Number(hr.pending_payroll || 0);
        const salaryPaidPct = netSalaries > 0 ? Math.min(100, Math.round((paidSalaries / netSalaries) * 100)) : 100;

        // Common Header Generator
        const renderHeader = (subtitle) => (
            <div>
                <div className="pdf-header-band d-flex justify-content-between align-items-center">
                    <div>
                        <div className="pdf-company-title">AMAS FARM ENTERPRISES LTD</div>
                        <div className="pdf-page-subtitle">Farm Performance Report | {subtitle}</div>
                    </div>
                    <div className="text-end text-white-50 small">
                        <div>Prepared {generatedOn}</div>
                        <div>Ref: {reportRefNo}</div>
                    </div>
                </div>
                <div className="pdf-gold-stripe"></div>
            </div>
        );

        // Common Footer Generator
        const renderFooter = (pageNum) => (
            <div className="pdf-footer d-flex justify-content-between text-muted">
                <span>AMAS FARM Performance Report - amounts in Tanzanian Shillings (TZS)</span>
                <span>Page {pageNum} of 4</span>
            </div>
        );

        return (
            <div className="official-report-document" ref={reportRef}>

                {/* ========================================================================= */}
                {/* PAGE 1: FINANCE OVERVIEW                                                  */}
                {/* ========================================================================= */}
                <div className="report-page">
                    <div>
                        {renderHeader("Finance Overview")}

                        {/* Plain English Lead Paragraph */}
                        <div className="pdf-lead-text my-4">
                            AMAS FARM brought in TZS {formatMoney(totalSales)} from sales and spent TZS {formatMoney(farmCosts)} running the farm, leaving TZS {formatMoney(netProfit)} in profit. Cash on hand across the safe, bank and mobile money comes to TZS {formatMoney(cashAvailable)}, and the farm owns TZS {formatMoney(totalWealth)} in equipment, machinery and stored feed.
                            <div className="pdf-sub-lead mt-1">
                                {dateRange.date_from || dateRange.date_to 
                                    ? `These figures cover the reporting window from ${moment(dateRange.date_from).format('D MMM YYYY')} to ${moment(dateRange.date_to).format('D MMM YYYY')}.`
                                    : "These figures cover every record in the system so far, not just one month."
                                }
                            </div>
                        </div>

                        {/* 4 Stat Cards in 2x2 Grid */}
                        <Row className="g-3 mb-4">
                            <Col xs={6}>
                                <div className="report-stat-card stripe-gold">
                                    <div className="stat-label">TOTAL SALES</div>
                                    <div className="stat-value">TZS {formatMoney(totalSales)}</div>
                                    <div className="stat-sublabel text-amber">Gross margin {f.gross_margin || '0.0%'}</div>
                                </div>
                            </Col>
                            <Col xs={6}>
                                <div className="report-stat-card stripe-red">
                                    <div className="stat-label">FARM COSTS</div>
                                    <div className="stat-value">TZS {formatMoney(farmCosts)}</div>
                                    <div className="stat-sublabel text-muted">Feed, running costs & wages</div>
                                </div>
                            </Col>
                            <Col xs={6}>
                                <div className="report-stat-card stripe-green">
                                    <div className="stat-label">NET PROFIT</div>
                                    <div className="stat-value">TZS {formatMoney(netProfit)}</div>
                                    <div className="stat-sublabel text-emerald">{salesKeptPct}% of sales kept</div>
                                </div>
                            </Col>
                            <Col xs={6}>
                                <div className="report-stat-card stripe-blue">
                                    <div className="stat-label">CASH AVAILABLE NOW</div>
                                    <div className="stat-value">TZS {formatMoney(cashAvailable)}</div>
                                    <div className="stat-sublabel text-secondary">Safe + bank + mobile money</div>
                                </div>
                            </Col>
                        </Row>

                        {/* Where the Money Went Section */}
                        <div className="report-section-banner">Where the Money Went</div>
                        <Row className="align-items-center g-4 mt-1">
                            <Col xs={6}>
                                <div style={{ width: '100%', height: 180 }}>
                                    <ResponsiveContainer>
                                        <BarChart 
                                            layout="vertical" 
                                            data={whereMoneyWentData} 
                                            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                                        >
                                            <XAxis type="number" hide />
                                            <YAxis dataKey="name" type="category" width={85} tick={{ fontSize: 10, fill: '#334155' }} />
                                            <Tooltip formatter={(val) => `TZS ${Number(val).toLocaleString()}`} />
                                            <Bar dataKey="amount" radius={[0, 4, 4, 0]} barSize={16} isAnimationActive={false}>
                                                {whereMoneyWentData.map((e, idx) => (
                                                    <Cell key={`bar-${idx}`} fill={e.fill} />
                                                ))}
                                                <LabelList dataKey="label" position="right" style={{ fontSize: 10, fill: '#475569', fontWeight: 600 }} />
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </Col>
                            <Col xs={6}>
                                <div className="pdf-narrative-text">
                                    <p className="mb-3">
                                        For every TZS 100 in sales, about TZS {cogsPer100} went to feed and stock, TZS {costsPer100} to running costs (electricity, fuel, repairs), TZS {wagesPer100} to wages, and TZS {profitPer100} was kept as profit.
                                    </p>
                                    <p className="mb-1 text-muted">
                                        <strong>Gross margin</strong> (before running costs and wages): {f.gross_margin || '0.0%'}
                                    </p>
                                    <p className="mb-0 text-muted">
                                        <strong>Net margin</strong> (after everything): {f.net_profit_margin || '0.0%'}
                                    </p>
                                </div>
                            </Col>
                        </Row>
                    </div>

                    {renderFooter(1)}
                </div>


                {/* ========================================================================= */}
                {/* PAGE 2: CASH & WHAT IS OWED                                              */}
                {/* ========================================================================= */}
                <div className="report-page">
                    <div>
                        {renderHeader("Cash & What Is Owed")}

                        <div className="report-section-banner mt-4">Cash & What Is Owed</div>
                        
                        <Row className="align-items-center g-4 my-2">
                            {/* Donut Chart with Centered Total */}
                            <Col xs={6}>
                                <div className="text-center">
                                    <div className="text-muted fw-bold small mb-2" style={{ fontSize: '0.78rem' }}>Where the farm's cash sits</div>
                                    <div style={{ position: 'relative', width: 170, height: 170, margin: '0 auto' }}>
                                        <PieChart width={170} height={170}>
                                            <Pie
                                                data={cashChartData}
                                                cx={85}
                                                cy={85}
                                                innerRadius={45}
                                                outerRadius={75}
                                                paddingAngle={3}
                                                dataKey="value"
                                                isAnimationActive={false}
                                            >
                                                {cashChartData.map((e, idx) => (
                                                    <Cell key={`cash-${idx}`} fill={e.fill} />
                                                ))}
                                            </Pie>
                                            <Tooltip formatter={(val) => `TZS ${Number(val).toLocaleString()}`} />
                                        </PieChart>
                                        <div style={{
                                            position: 'absolute',
                                            top: '50%',
                                            left: '50%',
                                            transform: 'translate(-50%, -50%)',
                                            textAlign: 'center',
                                            pointerEvents: 'none'
                                        }}>
                                            <div style={{ fontWeight: 800, fontSize: '0.85rem', color: '#1B4332' }}>
                                                TZS {(cashAvailable / 1000000).toFixed(2)}M
                                            </div>
                                            <div style={{ fontSize: '0.65rem', color: '#6B7280' }}>
                                                ready to use
                                            </div>
                                        </div>
                                    </div>

                                    {/* Donut Legend */}
                                    <div className="d-flex justify-content-center gap-3 mt-2 small" style={{ fontSize: '0.72rem' }}>
                                        <div><span style={{ color: '#F59E0B' }}>■</span> Farm Safe (TZS {formatMoney(cashSafe)})</div>
                                        <div><span style={{ color: '#2563EB' }}>■</span> Bank (TZS {formatMoney(bank)})</div>
                                        <div><span style={{ color: '#0D9488' }}>■</span> Mobile Money (TZS {formatMoney(mobileMoney)})</div>
                                    </div>
                                </div>
                            </Col>

                            {/* Money Owed Table & Highlighted Net Position */}
                            <Col xs={6}>
                                <div>
                                    <h6 className="fw-bold text-dark mb-3" style={{ fontSize: '0.95rem' }}>Money owed</h6>
                                    
                                    <div className="d-flex justify-content-between py-2 border-bottom" style={{ fontSize: '0.85rem' }}>
                                        <span className="text-secondary">Customers owe the farm</span>
                                        <span className="fw-bold font-monospace text-dark">TZS {formatMoney(customerOwed)}</span>
                                    </div>
                                    
                                    <div className="d-flex justify-content-between py-2 border-bottom" style={{ fontSize: '0.85rem' }}>
                                        <span className="text-secondary">The farm owes suppliers</span>
                                        <span className="fw-bold font-monospace text-dark">TZS {formatMoney(supplierPayable)}</span>
                                    </div>

                                    <div className="p-3 my-3 rounded" style={{ backgroundColor: '#F1F5F9', border: '1px solid #E2E8F0' }}>
                                        <div className="d-flex justify-content-between align-items-center">
                                            <span className="fw-bold text-dark" style={{ fontSize: '0.88rem' }}>Net position, after both</span>
                                            <div className="text-end">
                                                <div className="fw-bolder font-monospace text-dark fs-5">
                                                    TZS {formatMoney(netCashPosition)}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </Col>
                        </Row>

                        {/* Plain Language Liquidity Paragraph */}
                        <div className="pdf-narrative-text mt-4 p-3 rounded bg-light border">
                            {liquidityNarrative}
                        </div>
                    </div>

                    {renderFooter(2)}
                </div>


                {/* ========================================================================= */}
                {/* PAGE 3: POULTRY & EGG PRODUCTION                                         */}
                {/* ========================================================================= */}
                <div className="report-page">
                    <div>
                        {renderHeader("Poultry & Egg Production")}

                        {/* 4 Stat Cards in 2x2 Grid */}
                        <Row className="g-3 my-3">
                            <Col xs={6}>
                                <div className="report-stat-card stripe-gold">
                                    <div className="stat-label">EGGS HARVESTED</div>
                                    <div className="stat-value">{Number(eggsHarvested).toLocaleString()}</div>
                                    <div className="stat-sublabel text-secondary">All eggs collected</div>
                                </div>
                            </Col>
                            <Col xs={6}>
                                <div className="report-stat-card stripe-green">
                                    <div className="stat-label">GOOD FOR SALE</div>
                                    <div className="stat-value">{goodEggPct}%</div>
                                    <div className="stat-sublabel text-emerald">{Number(goodEggs).toLocaleString()} of {Number(eggsHarvested).toLocaleString()} eggs</div>
                                </div>
                            </Col>
                            <Col xs={6}>
                                <div className="report-stat-card stripe-gold">
                                    <div className="stat-label">DAILY LAYING RATE</div>
                                    <div className="stat-value">{o.average_laying_rate || '0.0%'}</div>
                                    <div className={`stat-sublabel ${layingRateNum >= 80 ? 'text-emerald' : 'text-amber'}`}>
                                        {layingRateNum >= 80 ? 'Within 80-90% norm' : 'Below 80-90% norm'}
                                    </div>
                                </div>
                            </Col>
                            <Col xs={6}>
                                <div className="report-stat-card stripe-red">
                                    <div className="stat-label">BIRDS LOST</div>
                                    <div className="stat-value">{Number(birdsLost).toLocaleString()}</div>
                                    <div className="stat-sublabel text-rose">Recorded this period</div>
                                </div>
                            </Col>
                        </Row>

                        {/* Egg Quality Section */}
                        <div className="report-section-banner">Egg Quality</div>
                        <Row className="align-items-center g-4 my-1">
                            <Col xs={5}>
                                <div className="text-center">
                                    <div style={{ position: 'relative', width: 140, height: 140, margin: '0 auto' }}>
                                        <PieChart width={140} height={140}>
                                            <Pie
                                                data={eggChartData}
                                                cx={70}
                                                cy={70}
                                                innerRadius={38}
                                                outerRadius={62}
                                                paddingAngle={3}
                                                dataKey="value"
                                                isAnimationActive={false}
                                            >
                                                {eggChartData.map((e, idx) => (
                                                    <Cell key={`egg-slice-${idx}`} fill={e.fill} />
                                                ))}
                                            </Pie>
                                            <Tooltip formatter={(val) => `${Number(val).toLocaleString()} eggs`} />
                                        </PieChart>
                                        <div style={{
                                            position: 'absolute',
                                            top: '50%',
                                            left: '50%',
                                            transform: 'translate(-50%, -50%)',
                                            textAlign: 'center',
                                            pointerEvents: 'none'
                                        }}>
                                            <div style={{ fontWeight: 800, fontSize: '0.82rem', color: '#10B981' }}>
                                                {goodEggPct}%
                                            </div>
                                            <div style={{ fontSize: '0.62rem', color: '#6B7280' }}>
                                                sellable
                                            </div>
                                        </div>
                                    </div>
                                    <div className="d-flex justify-content-center gap-3 mt-1 small" style={{ fontSize: '0.72rem' }}>
                                        <div><span style={{ color: '#10B981' }}>■</span> Good for sale ({Number(goodEggs).toLocaleString()})</div>
                                        <div><span style={{ color: '#EF4444' }}>■</span> Cracked/damaged ({Number(damagedEggs).toLocaleString()})</div>
                                    </div>
                                </div>
                            </Col>
                            <Col xs={7}>
                                <div className="pdf-narrative-text">
                                    Almost all eggs collected were good enough to sell. Only {Number(damagedEggs).toLocaleString()} out of {Number(eggsHarvested).toLocaleString()} came out cracked or damaged during collection.
                                </div>
                            </Col>
                        </Row>

                        {/* Housing & Feed Section */}
                        <div className="report-section-banner mt-3">Housing & Feed</div>
                        <div className="pdf-key-value-table">
                            <div className="kv-row d-flex justify-content-between">
                                <span className="text-secondary">Poultry houses in operation</span>
                                <span className="fw-bold text-dark">{o.active_houses || 0} houses</span>
                            </div>
                            <div className="kv-row d-flex justify-content-between">
                                <span className="text-secondary">Total housing capacity</span>
                                <span className="fw-bold text-dark">{Number(o.total_capacity || 0).toLocaleString()} birds</span>
                            </div>
                            <div className="kv-row d-flex justify-content-between">
                                <span className="text-secondary">Birds currently housed</span>
                                <span className="fw-bold text-dark">{Number(currentBirds).toLocaleString()} ({o.capacity_utilization || '0%'} of capacity used)</span>
                            </div>
                            <div className="kv-row d-flex justify-content-between">
                                <span className="text-secondary">Feed bought, all-time</span>
                                <span className="fw-bold text-dark font-monospace">TZS {formatMoney(o.feed_cost)}</span>
                            </div>
                            <div className="kv-row d-flex justify-content-between">
                                <span className="text-secondary">Feed used, most recent batch</span>
                                <span className="fw-bold text-dark">{o.feed_used || '0 kg'}</span>
                            </div>
                            <div className="kv-row d-flex justify-content-between">
                                <span className="text-secondary">Vaccination status</span>
                                <span className={`fw-bold ${Number(o.vaccinations_due || 0) > 0 ? 'text-amber' : 'text-emerald'}`}>
                                    {Number(o.vaccinations_due || 0) > 0 ? `${o.vaccinations_due} Due` : 'Up to date'}
                                </span>
                            </div>
                        </div>

                        {/* CRITICAL DATA INTEGRITY BOX */}
                        {hasContradiction ? (
                            <div className="report-alert-box mt-3 p-2 px-3 rounded">
                                <strong>Note:</strong> this report lists 0 birds currently on the farm, alongside {Number(birdsLost).toLocaleString()} birds recorded as lost and {Number(eggsHarvested).toLocaleString()} eggs collected overall. Worth checking whether that's a flock already cleared out between batches, or a gap in how the records were entered.
                            </div>
                        ) : (
                            <div className="report-note-box mt-3 p-2 px-3 rounded">
                                <strong>Flock Verification:</strong> {Number(currentBirds).toLocaleString()} live birds are currently active across {o.active_houses || 0} poultry houses with consistent daily production logging.
                            </div>
                        )}
                    </div>

                    {renderFooter(3)}
                </div>


                {/* ========================================================================= */}
                {/* PAGE 4: ASSETS, STOCK & SIGN-OFF                                         */}
                {/* ========================================================================= */}
                <div className="report-page">
                    <div>
                        {renderHeader("Assets, Stock & Team")}

                        {/* 3 Stat Cards in a row */}
                        <Row className="g-3 my-3">
                            <Col xs={4}>
                                <div className="report-stat-card stripe-slate">
                                    <div className="stat-label">EQUIPMENT & MACHINERY</div>
                                    <div className="stat-value">TZS {formatMoney(assetCost)}</div>
                                    <div className="stat-sublabel text-emerald">
                                        {assetPayable === 0 ? "Fully paid off" : `TZS ${formatMoney(assetPayable)} balance`}
                                    </div>
                                </div>
                            </Col>
                            <Col xs={4}>
                                <div className="report-stat-card stripe-gold">
                                    <div className="stat-label">FEED & SUPPLIES IN STORE</div>
                                    <div className="stat-value">TZS {formatMoney(stockValuation)}</div>
                                    <div className={`stat-sublabel ${lowStockCount === 0 ? 'text-emerald' : 'text-amber'}`}>
                                        {lowStockCount === 0 ? "Above reorder buffer" : `${lowStockCount} items low`}
                                    </div>
                                </div>
                            </Col>
                            <Col xs={4}>
                                <div className="report-stat-card stripe-slate">
                                    <div className="stat-label">TOTAL PHYSICAL WEALTH</div>
                                    <div className="stat-value">TZS {formatMoney(totalWealth)}</div>
                                    <div className="stat-sublabel text-secondary">Equipment + stock</div>
                                </div>
                            </Col>
                        </Row>

                        {/* What This Property Is Made Of */}
                        <div className="report-section-banner">What This Property Is Made Of</div>
                        <Row className="align-items-center g-4 my-1">
                            <Col xs={5}>
                                <div style={{ width: '100%', height: 160 }}>
                                    <ResponsiveContainer>
                                        <BarChart data={propertyBarData} margin={{ top: 20, right: 10, left: 10, bottom: 5 }}>
                                            <XAxis dataKey="name" tick={{ fontSize: 9, fill: '#475569' }} interval={0} />
                                            <YAxis hide />
                                            <Tooltip formatter={(val) => `TZS ${Number(val).toLocaleString()}`} />
                                            <Bar dataKey="amount" radius={[4, 4, 0, 0]} barSize={42} isAnimationActive={false}>
                                                {propertyBarData.map((e, idx) => (
                                                    <Cell key={`prop-${idx}`} fill={e.fill} />
                                                ))}
                                                <LabelList dataKey="displayVal" position="top" style={{ fontSize: 9, fontWeight: 700, fill: '#1E293B' }} />
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </Col>
                            <Col xs={7}>
                                <div className="pdf-narrative-text">
                                    About {propertyFractionText} of the farm's TZS {(totalWealth / 1000000).toFixed(2)} million in property is equipment and machinery. The rest is feed and supplies sitting in storage.
                                </div>
                            </Col>
                        </Row>

                        {/* Farm Team & Pay */}
                        <div className="report-section-banner mt-3">Farm Team & Pay</div>
                        <div className="pdf-key-value-table">
                            <div className="kv-row d-flex justify-content-between">
                                <span className="text-secondary">Active staff</span>
                                <span className="fw-bold text-dark">{hr.active_staff || 0} people</span>
                            </div>
                            <div className="kv-row d-flex justify-content-between">
                                <span className="text-secondary">Total salaries this period</span>
                                <span className="fw-bold text-dark font-monospace">TZS {formatMoney(netSalaries)}</span>
                            </div>
                            <div className="kv-row d-flex justify-content-between">
                                <span className="text-secondary">Already paid</span>
                                <span className="fw-bold text-dark font-monospace">TZS {formatMoney(paidSalaries)} ({salaryPaidPct}%)</span>
                            </div>
                            <div className="kv-row d-flex justify-content-between">
                                <span className="text-secondary">Pending balance</span>
                                <span className={`fw-bold font-monospace ${pendingSalaries > 0 ? 'text-danger' : 'text-dark'}`}>
                                    TZS {formatMoney(pendingSalaries)}
                                </span>
                            </div>
                        </div>

                        {/* Sign-Off Block */}
                        <div className="report-section-banner mt-3">Sign-Off</div>
                        <Row className="g-3 mt-1">
                            <Col xs={4}>
                                <div className="p-3 border rounded bg-white text-start">
                                    <div className="fw-bold text-dark small text-uppercase mb-1" style={{ fontSize: '0.78rem' }}>PREPARED BY</div>
                                    <div className="text-muted small">Farm Operations Supervisor</div>
                                    <div className="my-3 border-bottom"></div>
                                    <div className="text-muted small">Signature _________________</div>
                                    <div className="text-muted small mt-2">Date ______________________</div>
                                </div>
                            </Col>
                            <Col xs={4}>
                                <div className="p-3 border rounded bg-white text-start">
                                    <div className="fw-bold text-dark small text-uppercase mb-1" style={{ fontSize: '0.78rem' }}>VERIFIED & AUDITED BY</div>
                                    <div className="text-muted small">Finance & Accounts Manager</div>
                                    <div className="my-3 border-bottom"></div>
                                    <div className="text-muted small">Signature _________________</div>
                                    <div className="text-muted small mt-2">Date ______________________</div>
                                </div>
                            </Col>
                            <Col xs={4}>
                                <div className="p-3 border rounded bg-white text-start">
                                    <div className="fw-bold text-dark small text-uppercase mb-1" style={{ fontSize: '0.78rem' }}>APPROVED BY</div>
                                    <div className="text-muted small">Managing Director / Board</div>
                                    <div className="my-3 border-bottom"></div>
                                    <div className="text-muted small">Signature _________________</div>
                                    <div className="text-muted small mt-2">Date ______________________</div>
                                </div>
                            </Col>
                        </Row>
                    </div>

                    {renderFooter(4)}
                </div>

            </div>
        );
    };

    return (
        <div className="report-container">
            {/* Action Bar */}
            <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-3 d-print-none">
                <div className="d-block mb-2 mb-md-0">
                    <h4 className="fw-bold mb-1">Executive Farm Performance Report</h4>
                    <p className="text-muted mb-0 small">4-Page plain-language executive summary across Finance, Cash, Poultry & Capital Assets.</p>
                </div>
                <div className="btn-toolbar mb-2 mb-md-0">
                    <Button variant="primary" size="sm" onClick={handlePrint} disabled={!data || loading} className="shadow-sm">
                        <FontAwesomeIcon icon={faPrint} className="me-2" /> Print / Save Full Report (PDF)
                    </Button>
                </div>
            </div>

            {/* Filter Card */}
            <Card className="border-0 shadow-sm mb-4 d-print-none">
                <Card.Body className="py-2 px-3">
                    <Row className="align-items-end g-2">
                        <Col md={3}>
                            <Form.Group>
                                <Form.Label className="small fw-bold text-muted text-uppercase mb-1" style={{ fontSize: '0.75rem' }}>From Date</Form.Label>
                                <Form.Control 
                                    type="date" 
                                    size="sm"
                                    value={dateRange.date_from}
                                    onChange={(e) => setDateRange({...dateRange, date_from: e.target.value})}
                                />
                            </Form.Group>
                        </Col>
                        <Col md={3}>
                            <Form.Group>
                                <Form.Label className="small fw-bold text-muted text-uppercase mb-1" style={{ fontSize: '0.75rem' }}>To Date</Form.Label>
                                <Form.Control 
                                    type="date" 
                                    size="sm"
                                    value={dateRange.date_to}
                                    onChange={(e) => setDateRange({...dateRange, date_to: e.target.value})}
                                />
                            </Form.Group>
                        </Col>
                        <Col md={3}>
                            <div className="d-flex gap-2">
                                <Button 
                                    variant="primary" 
                                    size="sm" 
                                    className="w-100" 
                                    onClick={() => fetchSummary()} 
                                    disabled={loading}
                                >
                                    {loading ? <Spinner animation="border" size="sm" /> : "Filter Report"}
                                </Button>
                                <Button 
                                    variant="outline-secondary" 
                                    size="sm" 
                                    onClick={() => setQuickRange('all')}
                                    title="Reset Filter to All Time"
                                >
                                    <FontAwesomeIcon icon={faSyncAlt} />
                                </Button>
                            </div>
                        </Col>
                        <Col md={3} className="text-md-end">
                            <div className="btn-group btn-group-sm w-100">
                                <Button variant="outline-primary" size="sm" onClick={() => setQuickRange('today')}>Today</Button>
                                <Button variant="outline-primary" size="sm" onClick={() => setQuickRange('month')}>This Month</Button>
                                <Button variant="outline-primary" size="sm" onClick={() => setQuickRange('last30')}>30 Days</Button>
                                <Button variant="outline-primary" size="sm" onClick={() => setQuickRange('ytd')}>YTD</Button>
                            </div>
                        </Col>
                    </Row>
                </Card.Body>
            </Card>

            {error && <Alert variant="danger" className="d-print-none shadow-sm">{error}</Alert>}
            
            {loading ? (
                <div className="text-center py-5 d-print-none">
                    <Spinner animation="border" variant="primary" />
                    <p className="text-muted mt-2 small">Compiling executive farm report...</p>
                </div>
            ) : data ? (
                <div className="d-flex flex-column align-items-center pb-5">
                    {renderOfficialReport()}
                </div>
            ) : null}
            
            <style type="text/css">
                {`
                .official-report-document {
                    width: 100%;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                .report-page {
                    background: #ffffff;
                    width: 100%;
                    max-width: 210mm;
                    height: 297mm;
                    min-height: 297mm;
                    max-height: 297mm;
                    padding: 14mm 16mm;
                    margin-bottom: 20mm;
                    border-radius: 4px;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
                    border: 1px solid #e2e8f0;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    box-sizing: border-box;
                    overflow: hidden;
                }

                /* Header Band */
                .pdf-header-band {
                    background-color: #1B4332;
                    color: #ffffff;
                    padding: 10px 16px;
                    border-radius: 4px 4px 0 0;
                }
                .pdf-company-title {
                    font-size: 0.95rem;
                    font-weight: 800;
                    letter-spacing: 0.5px;
                }
                .pdf-page-subtitle {
                    font-size: 0.8rem;
                    color: #D1D5DB;
                }
                .pdf-gold-stripe {
                    height: 4px;
                    background-color: #D97706;
                    width: 100%;
                    border-radius: 0 0 4px 4px;
                }

                /* Section Banners */
                .report-section-banner {
                    background-color: #1B4332;
                    color: #ffffff;
                    font-size: 0.84rem;
                    font-weight: 700;
                    padding: 6px 12px;
                    border-radius: 4px;
                    letter-spacing: 0.3px;
                }

                /* Stat Cards */
                .report-stat-card {
                    background-color: #F8F9FA;
                    border: 1px solid #E5E7EB;
                    border-radius: 4px;
                    padding: 10px 14px;
                    position: relative;
                    overflow: hidden;
                }
                .report-stat-card::before {
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                }
                .stripe-gold::before { background-color: #D97706; }
                .stripe-red::before { background-color: #DC2626; }
                .stripe-green::before { background-color: #10B981; }
                .stripe-blue::before { background-color: #2563EB; }
                .stripe-slate::before { background-color: #64748B; }

                .stat-label {
                    font-size: 0.72rem;
                    text-transform: uppercase;
                    color: #6B7280;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                }
                .stat-value {
                    font-size: 1.35rem;
                    font-weight: 800;
                    color: #111827;
                    margin: 2px 0;
                    font-family: monospace, system-ui;
                }
                .stat-sublabel {
                    font-size: 0.78rem;
                    font-weight: 500;
                }
                .text-amber { color: #B45309; }
                .text-emerald { color: #059669; }
                .text-rose { color: #DC2626; }

                /* Lead text */
                .pdf-lead-text {
                    font-size: 0.88rem;
                    line-height: 1.45;
                    color: #1F2937;
                }
                .pdf-sub-lead {
                    font-size: 0.76rem;
                    color: #6B7280;
                    font-style: italic;
                }

                /* Narrative text */
                .pdf-narrative-text {
                    font-size: 0.84rem;
                    line-height: 1.45;
                    color: #374151;
                }

                /* Key Value Table */
                .pdf-key-value-table .kv-row {
                    padding: 6px 0;
                    border-bottom: 1px solid #F1F5F9;
                    font-size: 0.82rem;
                }

                /* Data Integrity Note Boxes */
                .report-alert-box {
                    background-color: #FFFBEB;
                    border: 1px solid #FCD34D;
                    color: #92400E;
                    font-size: 0.78rem;
                    line-height: 1.4;
                }
                .report-note-box {
                    background-color: #F0FDF4;
                    border: 1px solid #86EFAC;
                    color: #166534;
                    font-size: 0.78rem;
                    line-height: 1.4;
                }

                .pdf-footer {
                    font-size: 0.72rem;
                    border-top: 1px solid #E5E7EB;
                    padding-top: 8px;
                }

                @media print {
                    @page { 
                        size: A4 portrait; 
                        margin: 0; 
                    }
                    body { 
                        background: #ffffff !important; 
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                        color: #111827 !important;
                        margin: 0 !important;
                    }
                    .d-print-none, nav, aside, .sidebar, header, .navbar { 
                        display: none !important; 
                    }
                    .report-container, .content, main { 
                        width: 100% !important; 
                        margin: 0 !important; 
                        padding: 0 !important; 
                    }
                    .official-report-document {
                        width: 100% !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    .report-page { 
                        box-shadow: none !important; 
                        border: none !important;
                        border-radius: 0 !important;
                        margin: 0 !important;
                        padding: 10mm 14mm !important;
                        width: 210mm !important; 
                        height: 297mm !important;
                        max-height: 297mm !important;
                        min-height: 297mm !important; 
                        page-break-after: always !important;
                        break-after: page !important;
                        overflow: hidden !important;
                    }
                    .report-page:last-child {
                        page-break-after: avoid !important;
                        break-after: avoid !important;
                    }
                }
                `}
            </style>
        </div>
    );
};
