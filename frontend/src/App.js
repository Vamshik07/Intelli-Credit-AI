import React, { useEffect, useMemo, useState } from "react";

const FX_CACHE_KEY = "intelli_fx_rates_v1";
const FX_CACHE_TTL_MS = 4 * 60 * 60 * 1000;

const COUNTRY_TO_CURRENCY = {
  IN: "INR",
  US: "USD",
  GB: "GBP",
  EU: "EUR",
  DE: "EUR",
  FR: "EUR",
  IT: "EUR",
  ES: "EUR",
  CA: "CAD",
  AU: "AUD",
  JP: "JPY",
  SG: "SGD",
  AE: "AED",
};

const INDUSTRY_OPTIONS = [
  "Manufacturing",
  "Retail",
  "Technology",
  "Healthcare",
  "Infrastructure",
  "General",
];

const LOCATION_OPTIONS = [
  "Northern Economic Zone",
  "Southern Economic Zone",
  "Western Economic Zone",
  "Eastern Economic Zone",
  "Central Economic Zone",
  "Emerging Growth Zone",
];

const MARKET_TREND_OPTIONS = ["Growth", "Stable", "Volatile", "Declining"];

function detectCurrencyFromLocale() {
  const locale = navigator.language || "en-US";
  const region = locale.includes("-") ? locale.split("-")[1].toUpperCase() : "US";
  return COUNTRY_TO_CURRENCY[region] || "USD";
}

function parseNumber(value) {
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function App() {
  const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

  const [revenue, setRevenue] = useState("");
  const [profit, setProfit] = useState("");
  const [debt, setDebt] = useState("");
  const [industryType, setIndustryType] = useState("Manufacturing");
  const [locationZone, setLocationZone] = useState("Central Economic Zone");
  const [marketTrend, setMarketTrend] = useState("Stable");

  const [selectedCurrency, setSelectedCurrency] = useState(detectCurrencyFromLocale());
  const [rates, setRates] = useState({ USD: 1 });
  const [loadingRates, setLoadingRates] = useState(false);

  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const cachedRaw = localStorage.getItem(FX_CACHE_KEY);
    if (cachedRaw) {
      try {
        const cached = JSON.parse(cachedRaw);
        if (Date.now() - cached.timestamp < FX_CACHE_TTL_MS && cached.rates) {
          setRates(cached.rates);
          return;
        }
      } catch (error) {
        // Ignore bad cache and fetch fresh rates.
      }
    }

    const fetchRates = async () => {
      setLoadingRates(true);
      try {
        const response = await fetch("https://open.er-api.com/v6/latest/USD");
        const data = await response.json();

        if (data && data.rates) {
          setRates(data.rates);
          localStorage.setItem(
            FX_CACHE_KEY,
            JSON.stringify({ timestamp: Date.now(), rates: data.rates })
          );
        }
      } catch (error) {
        // Keep default USD-only rates if API fails.
      } finally {
        setLoadingRates(false);
      }
    };

    fetchRates();
  }, []);

  const currencyRate = rates[selectedCurrency] || 1;

  const formatter = useMemo(
    () =>
      new Intl.NumberFormat(undefined, {
        style: "currency",
        currency: selectedCurrency,
        maximumFractionDigits: 2,
      }),
    [selectedCurrency]
  );

  const handleSubmit = async () => {
    setErrorMessage("");

    const revenueLocal = parseNumber(revenue);
    const profitLocal = parseNumber(profit);
    const debtLocal = parseNumber(debt);

    if (revenueLocal <= 0 || debtLocal < 0) {
      setErrorMessage("Please enter valid revenue and debt values.");
      return;
    }

    const revenueUsd = revenueLocal / currencyRate;
    const profitUsd = profitLocal / currencyRate;
    const debtUsd = debtLocal / currencyRate;
    const debtRatio = revenueUsd ? debtUsd / revenueUsd : 0;

    try {
      const response = await fetch(`${apiBaseUrl}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          revenue: revenueUsd,
          profit: profitUsd,
          debt: debtUsd,
          industry_type: industryType,
          location_zone: locationZone,
          market_trend: marketTrend,
          debt_ratio: debtRatio,
        }),
      });

      if (!response.ok) {
        throw new Error("Prediction request failed");
      }

      const data = await response.json();
      setResult({
        ...data,
        revenueLocal,
        profitLocal,
        debtLocal,
        debtRatio,
      });
    } catch (error) {
      setErrorMessage("Unable to connect to backend. Please ensure API is running.");
    }
  };

  return (
    <div style={{ maxWidth: "760px", margin: "32px auto", fontFamily: "Segoe UI, sans-serif" }}>
      <h1>Intelli Credit AI</h1>
      <p>Credit scoring with regional and industry context.</p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
        <label>
          Revenue ({selectedCurrency})
          <input
            type="number"
            value={revenue}
            onChange={(e) => setRevenue(e.target.value)}
            style={{ width: "100%" }}
          />
        </label>

        <label>
          Profit ({selectedCurrency})
          <input
            type="number"
            value={profit}
            onChange={(e) => setProfit(e.target.value)}
            style={{ width: "100%" }}
          />
        </label>

        <label>
          Debt ({selectedCurrency})
          <input
            type="number"
            value={debt}
            onChange={(e) => setDebt(e.target.value)}
            style={{ width: "100%" }}
          />
        </label>

        <label>
          Display Currency
          <select
            value={selectedCurrency}
            onChange={(e) => setSelectedCurrency(e.target.value)}
            style={{ width: "100%" }}
          >
            {Object.keys(rates)
              .sort()
              .map((currencyCode) => (
                <option key={currencyCode} value={currencyCode}>
                  {currencyCode}
                </option>
              ))}
          </select>
        </label>

        <label>
          Industry Type
          <select
            value={industryType}
            onChange={(e) => setIndustryType(e.target.value)}
            style={{ width: "100%" }}
          >
            {INDUSTRY_OPTIONS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>

        <label>
          Applicant Location Zone
          <select
            value={locationZone}
            onChange={(e) => setLocationZone(e.target.value)}
            style={{ width: "100%" }}
          >
            {LOCATION_OPTIONS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>

        <label>
          Market Trend
          <select
            value={marketTrend}
            onChange={(e) => setMarketTrend(e.target.value)}
            style={{ width: "100%" }}
          >
            {MARKET_TREND_OPTIONS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
      </div>

      <button onClick={handleSubmit} style={{ marginTop: "16px", padding: "10px 18px" }}>
        Check Credit Risk
      </button>

      {loadingRates && <p>Updating currency rates...</p>}
      {errorMessage && <p style={{ color: "#c62828" }}>{errorMessage}</p>}

      {result && (
        <div style={{ marginTop: "20px", padding: "14px", border: "1px solid #ddd" }}>
          <h2>Prediction: {result.prediction}</h2>
          <p>Risk Score: {result.risk_score}%</p>
          <p>{result.explanation}</p>
          <p>
            Debt Ratio: <strong>{result.debtRatio.toFixed(2)}</strong>
          </p>
          <p>
            Revenue: <strong>{formatter.format(result.revenueLocal)}</strong>
          </p>
          <p>
            Profit: <strong>{formatter.format(result.profitLocal)}</strong>
          </p>
          <p>
            Debt: <strong>{formatter.format(result.debtLocal)}</strong>
          </p>
        </div>
      )}
    </div>
  );
}

export default App;
